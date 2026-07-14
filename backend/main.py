from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

from database import get_db, Interaction
from agent import app_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request_data: ChatRequest):
    user_message = request_data.message
    
    # Run the agent
    inputs = {"messages": [("user", user_message)]}
    result = app_agent.invoke(inputs)
    
    # Extract the final text response (which should be JSON string)
    final_text = result["messages"][-1].content
    
    # Extract tool usage for the frontend
    executed_tools = []
    for msg in reversed(result["messages"]):
        if isinstance(msg, HumanMessage):
            break
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool in msg.tool_calls:
                executed_tools.append({
                    "name": tool["name"],
                    "args": tool["args"]
                })

    return {
        "response": final_text,
        "tools_used": executed_tools
    }

@app.get("/api/interactions")
def get_interactions(db: Session = Depends(get_db)):
    return db.query(Interaction).all()