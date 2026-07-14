# CRM HCP Assessment Assistant

## Introduction

The **CRM HCP Assessment Assistant** is an intelligent, full-stack application designed for pharmaceutical representatives to manage their interactions with Healthcare Professionals (HCPs). By combining a **FastAPI** backend, a **LangGraph** intelligence layer powered by **Groq (Llama 3.3)**, and a **React + Redux** frontend, the system allows users to update their CRM entirely through natural language.

Instead of manually clicking through complex forms, a representative can simply type what happened during their day (e.g., *"Met Dr. Smith today to drop off 5 samples of Product X and it went great"*), and the AI automatically extracts the details, updates the structured CRM database, and syncs the UI in real time.

---

## Functionalities

* **Intelligent Interaction Logging:** Extracts the HCP's name, automatically infers the interaction type (meeting, call, email), determines customer sentiment (positive, neutral, negative), and commits it to the database.
* **Context-Aware Smart Editing:** Searches for existing doctors using a flexible matching mechanism and updates *only* the specific fields requested by the user, leaving other data intact.
* **Smart Scheduling:** Understands scheduling requests (e.g., *"Schedule a follow-up call in 3 days"*) and logs a calendar event to the database.
* **Sample Tracking:** Tracks product names and quantities distributed during field visits.
* **Dynamic UI Autofill:** The React frontend intercepts the AI's internal reasoning, maps the data, and automatically fills out or updates the manual form fields in real-time as the user chats.

---

## Cloning and Installation Process

### **Prerequisites**

* Python 3.10 or higher
* Node.js (v18 or higher) and npm
* A Groq API Key

### **1. Clone the Repository**

```bash
git clone https://github.com/mohdshahid192-guthub/CRM-HCP-Assessment.git
cd CRM-HCP-Assesment

```

### **2. Backend Setup**

Navigate to the backend directory, set up a virtual environment, and install dependencies.

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv langchain-core langchain-groq langgraph

```

Create a `.env` file in the `backend` directory:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
DATABASE_URL=sqlite:///crm_app.db

```

*(Note: The database defaults to a local SQLite instance `crm_app.db` for zero-configuration local testing. You can change this string to your MySQL production instance when ready).*

### **3. Frontend Setup**

Open a new terminal window, navigate to the frontend directory, and install the npm packages.

```bash
cd frontend
npm install

```

---

## How to Use

### **1. Start the Backend Server**

From your backend directory (with the virtual environment activated), start the Uvicorn development server:

```bash
uvicorn main:app --reload

```

The server will start running at `http://127.0.0.1:8000`.

### **2. Start the Frontend Application**

From your frontend directory, start the React development server:

```bash
npm start

```

The application will open automatically in your browser at `http://localhost:3000`.

### **3. Interacting with the Assistant**

Open the application interface. You will see a structured CRM form on the left and an AI Assistant chat panel on the right. Try entering the following phrases into the chat to see the application in action:

* **To Log:** *"I had a meeting with Dr. Alex Smith about Product X. It was a positive interaction."*
* *Result:* The form will auto-populate with Dr. Alex Smith, set the type to "Meeting", select "Positive", and create a database entry.


* **To Edit:** *"Actually, change the sentiment of my last interaction with Dr. Smith to negative."*
* *Result:* The backend uses a close-match lookup to locate the latest entry for Dr. Alex Smith, updates *only* the sentiment field to "Negative" in the database, and reflects the change immediately in the frontend form.


* **To Schedule:** *"Schedule a follow-up call with Dr. Smith in 5 days."*
* *Result:* Creates a calendar record inside the `schedules` table for 5 days from the current date.
