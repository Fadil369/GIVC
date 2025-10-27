"""
🌐 MCP Gateway Service
OID: 1.3.6.1.4.1.61026.8.1

Message Context Protocol gateway for routing between LINC agents.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import httpx
import hmac
import hashlib
import json
import os
import redis
from datetime import datetime

# Configuration
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://oid-registry:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://:brainsait2024@redis:6379/1")
MCP_SECRET = os.getenv("MCP_SECRET_KEY", "mcp_secret_2024")

# Redis
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Pydantic Models
class MCPMessage(BaseModel):
    from_agent: str
    to_agent: str
    type: str  # request, response, event
    payload: Dict
    signature: Optional[str] = None

class WorkflowStep(BaseModel):
    agent: str
    action: str
    params: Optional[Dict] = {}

# FastAPI App
app = FastAPI(title="BrainSAIT MCP Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def sign_message(message: Dict) -> str:
    """Generate HMAC signature for message"""
    payload = json.dumps(message, sort_keys=True)
    return hmac.new(MCP_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()

def verify_signature(message: Dict, signature: str) -> bool:
    """Verify message signature"""
    expected = sign_message(message)
    return hmac.compare_digest(expected, signature)

async def get_agent_endpoint(oid: str) -> Optional[str]:
    """Get agent endpoint from registry"""
    cache_key = f"endpoint:{oid}"
    
    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return cached
    
    # Fetch from registry
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{REGISTRY_URL}/api/v1/registry/agents/{oid}")
            if response.status_code == 200:
                agent = response.json()
                endpoint = agent.get("endpoints", {}).get("rest")
                if endpoint:
                    redis_client.setex(cache_key, 300, endpoint)
                return endpoint
        except:
            return None

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp-gateway"}

@app.post("/route")
async def route_message(message: MCPMessage):
    """Route message from one agent to another"""
    
    # Get target endpoint
    endpoint = await get_agent_endpoint(message.to_agent)
    if not endpoint:
        raise HTTPException(404, f"Agent {message.to_agent} not found")
    
    # Sign message
    msg_dict = message.model_dump()
    msg_dict["signature"] = sign_message(msg_dict)
    msg_dict["timestamp"] = datetime.utcnow().isoformat()
    
    # Route to endpoint
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{endpoint}/mcp/receive",
                json=msg_dict,
                headers={"X-MCP-From": message.from_agent}
            )
            return response.json()
        except httpx.TimeoutException:
            raise HTTPException(504, "Target agent timeout")
        except Exception as e:
            raise HTTPException(500, f"Routing error: {str(e)}")

@app.post("/orchestrate")
async def orchestrate_workflow(workflow: List[WorkflowStep]):
    """Execute multi-agent workflow"""
    
    context = {}
    results = []
    
    for step in workflow:
        message = MCPMessage(
            from_agent="orchestrator",
            to_agent=step.agent,
            type="request",
            payload={"action": step.action, "params": step.params, "context": context}
        )
        
        try:
            result = await route_message(message)
            results.append(result)
            context.update(result.get("context", {}))
        except Exception as e:
            return {"status": "failed", "step": step.agent, "error": str(e), "completed": results}
    
    return {"status": "success", "results": results, "final_context": context}

@app.get("/agents")
async def list_agents():
    """List all registered agents"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{REGISTRY_URL}/api/v1/registry/agents")
        return response.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
