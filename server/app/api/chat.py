from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from app.graph.edges import graph

router = APIRouter()

class EnvironmentContext(BaseModel):
    rainfall: Optional[float] = None
    soil_organic_carbon: Optional[float] = None
    land_use: Optional[str] = None
    
class LocationContext(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    environment: Optional[EnvironmentContext] = None
    location: Optional[LocationContext] = None

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    conv_id = request.conversation_id or str(uuid.uuid4())
    
    # Save the user's message if we're persisting messages
    # (The load_conversation node does this on initialization)
    from app.db.supabase import save_message
    save_message(conv_id, {"role": "user", "content": request.message})
    
    # Build environmental context
    env_ctx = {}
    if request.environment:
        env_ctx["climate"] = {"rainfall": request.environment.rainfall}
        env_ctx["soil"] = {"organic_carbon": request.environment.soil_organic_carbon}
        env_ctx["land"] = {"land_use": request.environment.land_use}
    if request.location:
        env_ctx["location"] = request.location.model_dump()
        
    initial_state = {
        "conversation_id": conv_id,
        "user_query": request.message,
        "environmental_context": env_ctx
    }
    
    try:
        final_state = graph.invoke(initial_state)
        # Extract response
        return final_state.get("final_response", {
            "conversation_id": conv_id,
            "answer": "Failed to generate a response.",
            "recommendations": [],
            "clarification_required": False
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
