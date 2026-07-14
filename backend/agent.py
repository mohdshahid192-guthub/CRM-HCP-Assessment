import os
import difflib
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

# Import database session and models
from database import SessionLocal, Interaction, Schedule, Sample

load_dotenv()
my_groq_key = os.getenv("GROQ_API_KEY")

# --- Helper: Vector Search Mock ---
def vector_search_hcp(session, search_name: str) -> str:
    """Simulates a Vector Search by finding the closest matching HCP name in the database."""
    all_interactions = session.query(Interaction.hcp_name).distinct().all()
    all_names = [record[0] for record in all_interactions if record[0]]
    if not all_names:
        return search_name
    matches = difflib.get_close_matches(search_name, all_names, n=1, cutoff=0.4)
    return matches[0] if matches else search_name

# --- AI Tools ---
@tool
def log_interaction(hcp_name: str, interaction_type: str, discussion_topics: str, sentiment: str) -> dict:
    """Logs a new interaction and saves it to the database."""
    db = SessionLocal()
    try:
        new_interaction = Interaction(
            hcp_name=hcp_name,
            interaction_type=interaction_type,
            topics=discussion_topics,
            sentiment=sentiment
        )
        db.add(new_interaction)
        db.commit()
        db.refresh(new_interaction)
        return {
            "hcp_name": new_interaction.hcp_name,
            "interaction_type": new_interaction.interaction_type,
            "discussion_topics": new_interaction.topics,
            "sentiment": new_interaction.sentiment,
            "message": f"Successfully logged new interaction for {hcp_name} in database."
        }
    finally:
        db.close()

@tool
def edit_interaction(hcp_name: str, new_interaction_type: str = None, new_topics: str = None, new_sentiment: str = None) -> dict:
    """Searches for the latest interaction with a doctor and updates ONLY the provided fields."""
    db = SessionLocal()
    try:
        matched_name = vector_search_hcp(db, hcp_name)
        interaction = db.query(Interaction).filter(Interaction.hcp_name == matched_name).order_by(Interaction.date.desc()).first()
        
        if not interaction:
            return {"error": f"Could not find any past interactions for {matched_name} to edit."}
            
        if new_interaction_type: interaction.interaction_type = new_interaction_type
        if new_topics: interaction.topics = new_topics
        if new_sentiment: interaction.sentiment = new_sentiment
        
        db.commit()
        db.refresh(interaction)
        
        return {
            "hcp_name": interaction.hcp_name,
            "interaction_type": interaction.interaction_type,
            "discussion_topics": interaction.topics,
            "sentiment": interaction.sentiment,
            "message": f"Successfully updated the latest interaction for {matched_name}."
        }
    finally:
        db.close()

@tool
def schedule_interaction(hcp_name: str, schedule_type: str, days_from_now: int) -> dict:
    """Schedules a future meeting, call, or email."""
    db = SessionLocal()
    try:
        target_date = datetime.utcnow() + timedelta(days=days_from_now)
        new_schedule = Schedule(hcp_name=hcp_name, schedule_type=schedule_type, scheduled_date=target_date)
        db.add(new_schedule)
        db.commit()
        return {"hcp_name": hcp_name, "schedule_type": schedule_type, "message": f"Scheduled a {schedule_type} with {hcp_name}."}
    finally:
        db.close()

@tool
def record_samples(hcp_name: str, sample_name: str, quantity: int) -> dict:
    """Records product samples dropped off to the HCP."""
    db = SessionLocal()
    try:
        new_sample = Sample(hcp_name=hcp_name, sample_name=sample_name, quantity=quantity)
        db.add(new_sample)
        db.commit()
        return {"hcp_name": hcp_name, "sample_name": sample_name, "quantity": quantity, "message": f"Recorded {quantity} {sample_name} for {hcp_name}."}
    finally:
        db.close()

@tool
def get_hcp(hcp_name: str) -> dict:
    """Returns the LATEST interaction for this doctor."""
    db = SessionLocal()
    try:
        matched_name = vector_search_hcp(db, hcp_name)
        interaction = db.query(Interaction).filter(Interaction.hcp_name == matched_name).order_by(Interaction.date.desc()).first()
        if not interaction:
            return {"message": f"No interactions found for {matched_name}."}
        return {
            "hcp_name": interaction.hcp_name,
            "interaction_type": interaction.interaction_type,
            "discussion_topics": interaction.topics,
            "sentiment": interaction.sentiment,
            "message": f"Retrieved latest profile data for {matched_name}."
        }
    finally:
        db.close()

# --- Agent Build ---
tools = [log_interaction, edit_interaction, schedule_interaction, record_samples, get_hcp]

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], lambda a, b: a + b]

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=my_groq_key)
llm_with_tools = llm.bind_tools(tools)

system_prompt = SystemMessage(content="""
You are an intelligent CRM database assistant. Follow these rules based on user input:
1. "Log interaction": Call `log_interaction`.
2. "Edit interaction": Call `edit_interaction`. Pass ONLY the fields the user explicitly wants to change.
3. "Schedule": Call `schedule_interaction`.
4. "Record/Drop sample": Call `record_samples`.
5. "Get/Info on HCP": Call `get_hcp`.

CRITICAL: When the tool finishes, you MUST output a raw JSON object matching the exact data returned by the tool. DO NOT output conversational text, markdown formatting, or ```json. Output ONLY the raw JSON dictionary.
""")

def call_model(state: AgentState):
    messages = [system_prompt] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", lambda state: "tools" if state["messages"][-1].tool_calls else END)
workflow.add_edge("tools", "agent")

app_agent = workflow.compile()