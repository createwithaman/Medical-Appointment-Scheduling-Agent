# Appointment Scheduling App

## Features

### Core Feature 1: Calendly Integration
- Mock Calendly API for appointment scheduling
- Multiple appointment types with correct durations:
  - General Consultation: 30 minutes
  - Follow-up: 15 minutes
  - Physical Exam: 45 minutes
  - Specialist Consultation: 60 minutes
-  Smart availability detection
-  Conflict prevention (no double-booking)
-  Time slot recommendations based on preferences

### Intelligent Agent
-  Natural, empathetic conversation flow
-  Seamless context switching (FAQ ↔ Scheduling)
-  Tool calling for availability checks and bookings
-  Edge case handling (no slots, invalid dates, API failures)
-  Smart slot recommendations based on preferences

##  Architecture

```
User Request → FastAPI → Scheduling Agent (GPT-4)
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
            RAG System              Calendly API
          (ChromaDB + GPT)         (Mock Backend)
                    ↓                   ↓
              FAQ Answer         Available Slots
                    ↓                   ↓
                    └─────────┬─────────┘
                              ↓
                      Natural Response


##  Project Structure


appointment-scheduling-agent/
├── README.md
├── .env
├── requirements.txt
├── backend/
│   ├── main.py
│   ├── agent/
│   │   ├── scheduling_agent.py
│   │   └── prompts.py
│   ├── rag/
│   │   ├── faq_rag.py
│   │   ├── embeddings.py
│   │   └── vector_store.py
│   ├── api/
│   │   ├── chat.py
│   │   └── calendly_integration.py
│   ├── tools/
│   │   ├── availability_tool.py
│   │   └── booking_tool.py
│   └── models/
│       └── schemas.py
├── frontend/
│   └── gradio_app.py
└── data/
    ├── clinic_info.json
    ├── doctor_schedule.json
    └── bookings.json

```

##  Setup Instructions

### Prerequisites
- Python 3.11
- OpenAI API Key
- pip package manager


### Manual Setup

1. *Clone the repository*
bash
git clone https://github.com/createwithaman/Medical-Appointment-Scheduling-Agent.git
cd /folder_name


2. *Create virtual environment*
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


3. *Install dependencies*
pip install -r requirements.txt


4. *Set up environment variables*
# Edit .env and add your OPENAI_API_KEY

5. *Run the backend*
uvicorn backend.main:app --reload --port 8000

6. *Run the UI*

# In a new terminal
source venv/bin/activate
python frontend/gradio_app.py


### Access Points

- *Backend API:* http://localhost:8000
- *API Documentation:* http://localhost:8000/docs
- *Gradio UI:* http://localhost:7860

##  API Documentation

### Interactive Docs
-  http://localhost:8000/docs


### Main Endpoints

#### 1. *POST /api/chat*
Main conversational endpoint for scheduling and FAQ

### Example Conversations

#### Conversation 1: Successful Booking

User: I need to see the doctor
Agent: I'd be happy to help you schedule an appointment! What's the main reason for your visit today?

User: I've been having headaches
Agent: I understand. For persistent headaches, I'd recommend a general consultation (30 minutes)...

User: Afternoon if possible, sometime this week
Agent: Let me check our afternoon availability this week...


##  System Design

### Agent Conversation Flow
1. *Understanding Phase*: Greet and understand patient needs
2. *Classification*: Determine if FAQ or scheduling request
3. *Tool Execution*: Call appropriate tools (RAG search or availability check)
4. *Slot Recommendation*: Suggest 3-5 slots based on preferences
5. *Information Collection*: Gather patient details
6. *Confirmation*: Confirm and book appointment

### RAG Pipeline for FAQs
1. *Ingestion*: Load clinic_info.json into ChromaDB
2. *Embedding*: Use OpenAI text-embedding-3-small
3. *Retrieval*: Semantic search with top-k=3
4. *Generation*: GPT-4 generates grounded answers
5. *Validation*: Ensure no hallucination

### Scheduling Logic
- *Available Slots Determination*: Check doctor schedule vs existing bookings
- *Appointment Type Handling*: Match duration with slot availability
- *Conflict Prevention*: Validate no overlapping appointments
- *Buffer Time*: 5-minute buffer between appointments
- *Business Hours*: Mon-Sat, 9:00 AM - 6:00 PM (lunch 1-2 PM)


##  Edge Cases Covered

### No Available Slots
- Clearly explain situation
- Offer alternative dates
- Suggest calling office for urgent needs

### Invalid Input
- Non-existent dates
- Past dates
- Outside business hours
- Proper error messages

### API Failures
- Graceful degradation
- Informative error messages
- Fallback suggestions


