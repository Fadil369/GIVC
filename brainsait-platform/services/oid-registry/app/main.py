"""
🔐 OID Registry Service
OID: 1.3.6.1.4.1.61026.2.1

Central registry for all LINC agents in the BrainSAIT ecosystem.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, JSON, DateTime, Text, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import os
import redis
import json

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://brainsait:brainsait_secure_2024@postgres:5432/registry")
REDIS_URL = os.getenv("REDIS_URL", "redis://:brainsait2024@redis:6379/0")
OID_ROOT = os.getenv("OID_ROOT", "1.3.6.1.4.1.61026")

# Database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AgentModel(Base):
    __tablename__ = "agents"
    
    oid = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    version = Column(String, nullable=False)
    status = Column(String, default="active")
    endpoints = Column(JSON, nullable=False)
    capabilities = Column(ARRAY(Text))
    dependencies = Column(ARRAY(Text))
    agent_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Redis
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Pydantic Models
class AgentEndpoints(BaseModel):
    rest: Optional[str] = None
    websocket: Optional[str] = None

class AgentCreate(BaseModel):
    oid: str
    name: str
    domain: str
    version: str = "1.0.0"
    status: str = "active"
    endpoints: AgentEndpoints
    capabilities: List[str] = []
    dependencies: List[str] = []
    metadata: Optional[Dict] = {}

class AgentResponse(AgentCreate):
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# FastAPI App
app = FastAPI(title="BrainSAIT OID Registry", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
async def health_check():
    try:
        redis_client.ping()
        return {"status": "healthy", "service": "oid-registry"}
    except:
        return {"status": "degraded", "service": "oid-registry"}

@app.post("/api/v1/registry/agents", response_model=AgentResponse)
async def register_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    if not agent.oid.startswith(OID_ROOT):
        raise HTTPException(400, f"OID must start with {OID_ROOT}")
    
    existing = db.query(AgentModel).filter(AgentModel.oid == agent.oid).first()
    if existing:
        raise HTTPException(409, f"Agent {agent.oid} already exists")
    
    db_agent = AgentModel(**agent.model_dump())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    redis_client.setex(f"agent:{agent.oid}", 3600, json.dumps(agent.model_dump()))
    return db_agent

@app.get("/api/v1/registry/agents", response_model=List[AgentResponse])
async def list_agents(domain: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AgentModel)
    if domain:
        query = query.filter(AgentModel.domain == domain)
    return query.all()

@app.get("/api/v1/registry/agents/{oid}", response_model=AgentResponse)
async def get_agent(oid: str, db: Session = Depends(get_db)):
    agent = db.query(AgentModel).filter(AgentModel.oid == oid).first()
    if not agent:
        raise HTTPException(404, f"Agent {oid} not found")
    return agent

@app.get("/api/v1/registry/depends/{oid}")
async def get_dependencies(oid: str, db: Session = Depends(get_db)):
    agent = db.query(AgentModel).filter(AgentModel.oid == oid).first()
    if not agent:
        raise HTTPException(404, f"Agent {oid} not found")
    
    dependencies = []
    for dep_oid in agent.dependencies:
        dep = db.query(AgentModel).filter(AgentModel.oid == dep_oid).first()
        if dep:
            dependencies.append({"oid": dep.oid, "name": dep.name, "version": dep.version})
    
    return {"agent": {"oid": agent.oid, "name": agent.name}, "dependencies": dependencies}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
