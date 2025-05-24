from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import asyncio
import os
from pathlib import Path
from datetime import datetime

from agents.tutor_agent import TutorAgent
from agents.math_agent import MathAgent
from agents.physics_agent import PhysicsAgent
from core.base_agent import AgentMessage, AgentContext
from core.state_manager import state_manager

app = FastAPI(title="AI Tutor Multi-Agent System", version="1.0.0")

# Create directories if they don't exist
def ensure_directories():
    directories = ["static", "templates", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

ensure_directories()

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize agents with Gemini 2.0 Flash
tutor_agent = TutorAgent()
math_agent = MathAgent()
physics_agent = PhysicsAgent()

# Register specialists with tutor
tutor_agent.register_specialist("math", math_agent)
tutor_agent.register_specialist("physics", physics_agent)

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    session_id: str
    agent_used: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # Create or get session
        session_id = request.session_id or await state_manager.create_session()
        
        # Get session context
        session_data = await state_manager.get_session(session_id)
        if not session_data:
            session_id = await state_manager.create_session()
            session_data = await state_manager.get_session(session_id)
        
        # Create context
        context = AgentContext(
            session_id=session_id,
            user_query=request.query,
            conversation_history=session_data["conversation_history"],
            current_step=len(session_data["conversation_history"]) + 1,
            workflow_state=session_data.get("context", {})
        )
        
        # Create message
        message = AgentMessage(
            id=f"msg_{session_id}_{context.current_step}",
            sender_id="user",
            receiver_id=tutor_agent.agent_id,
            content=request.query,
            message_type="query",
            timestamp=datetime.now()
        )
        
        # Process with tutor agent
        response = await tutor_agent.process(message, context)
        
        # Update session
        await state_manager.add_to_history(session_id, "user", request.query)
        await state_manager.add_to_history(session_id, "assistant", response)
        
        return QueryResponse(
            response=response,
            session_id=session_id,
            agent_used=tutor_agent.name
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/session/new", response_model=dict)
async def create_new_session():
    try:
        # Create new session
        session_id = await state_manager.create_session()
        
        # Get session context
        session_data = await state_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=500, detail="Failed to create session")
            
        return {
            "session_id": session_id,
            "created_at": session_data["created_at"],
            "message": "New session created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    session_data = await state_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_data

@app.get("/api/agents")
async def get_agents():
    return {
        "tutor": {
            "id": tutor_agent.agent_id,
            "name": tutor_agent.name,
            "type": tutor_agent.agent_type.value
        },
        "specialists": {
            "math": {
                "id": math_agent.agent_id,
                "name": math_agent.name,
                "capabilities": math_agent.capabilities,
                "tools": [tool.name for tool in math_agent.tools]
            },
            "physics": {
                "id": physics_agent.agent_id,
                "name": physics_agent.name,
                "capabilities": physics_agent.capabilities,
                "tools": [tool.name for tool in physics_agent.tools]
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
