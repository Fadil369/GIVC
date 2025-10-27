"""
💬 Chat Engine Service
OID: 1.3.6.1.4.1.61026.7.1

AI-powered chat service with context awareness and template integration.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from typing import List, Dict
from datetime import datetime
import json
import os
import redis

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MCP_GATEWAY_URL = os.getenv("MCP_GATEWAY_URL", "http://mcp-gateway:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://:brainsait2024@redis:6379/3")

# Redis
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# OpenAI
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# FastAPI App
app = FastAPI(title="BrainSAIT Chat Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "chat-engine",
        "openai_configured": bool(OPENAI_API_KEY)
    }

@app.websocket("/chat/{session_id}")
async def chat_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    
    # Get conversation history
    history_key = f"chat:{session_id}:history"
    history = []
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            user_message = data.get("message", "")
            
            if not user_message:
                continue
            
            # Add to history
            history.append({"role": "user", "content": user_message})
            
            # Save to Redis
            redis_client.rpush(history_key, json.dumps({"role": "user", "content": user_message}))
            redis_client.expire(history_key, 3600)  # 1 hour
            
            # Generate response
            if openai_client:
                response_text = await generate_ai_response(history)
            else:
                response_text = f"Echo: {user_message} (AI not configured)"
            
            # Add assistant response to history
            history.append({"role": "assistant", "content": response_text})
            redis_client.rpush(history_key, json.dumps({"role": "assistant", "content": response_text}))
            
            # Send response
            await manager.send_message(session_id, {
                "type": "message",
                "content": response_text,
                "timestamp": str(datetime.utcnow())
            })
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "error",
            "message": str(e)
        })
        manager.disconnect(session_id)

async def generate_ai_response(history: List[Dict]) -> str:
    """Generate AI response using OpenAI"""
    
    system_prompt = """You are BrainSAIT Assistant, an AI companion for learning and productivity.
You help users with:
- Learning new skills
- Finding templates and resources
- Automating workflows
- Healthcare guidance (GIVC platform)

Be concise, helpful, and supportive."""
    
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                *history
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

@app.get("/chat/{session_id}/history")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    history_key = f"chat:{session_id}:history"
    messages = redis_client.lrange(history_key, 0, -1)
    
    return {
        "session_id": session_id,
        "messages": [json.loads(msg) for msg in messages]
    }

if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    uvicorn.run(app, host="0.0.0.0", port=8000)
