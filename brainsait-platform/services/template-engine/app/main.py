#!/usr/bin/env python3
"""
TemplateLINC - Template Management Engine
OID: 1.3.6.1.4.1.61026.6.1
Integrates with Notion API for template syncing and management
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, String, Text, DateTime, ARRAY, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
import httpx
import os
import logging
import redis
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TemplateLINC",
    description="Template Management Engine - Notion Integration",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")
NOTION_API_VERSION = "2022-06-28"
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://oid-registry:8000")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://brainsait:brainsait_secure_2024@postgres:5432/brainsait")
REDIS_URL = os.getenv("REDIS_URL", "redis://:brainsait2024@redis:6379/2")

# Database setup
Base = declarative_base()

class TemplateModel(Base):
    __tablename__ = "templates"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    tags = Column(ARRAY(Text))
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Redis client
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Models
class Template(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    category: str
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TemplateQuery(BaseModel):
    query: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 10

class SyncRequest(BaseModel):
    force: bool = False

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Cache helper
def cache_template(template_id: str, template: Template, ttl: int = 300):
    """Cache template in Redis"""
    try:
        import json
        redis_client.setex(f"template:{template_id}", ttl, template.model_dump_json())
    except Exception as e:
        logger.warning(f"Redis cache failed: {e}")

def get_cached_template(template_id: str) -> Optional[Template]:
    """Get template from cache"""
    try:
        import json
        cached = redis_client.get(f"template:{template_id}")
        if cached:
            return Template(**json.loads(cached))
    except Exception as e:
        logger.warning(f"Redis get failed: {e}")
    return None

# Notion API client
async def notion_request(method: str, endpoint: str, data: Optional[Dict] = None):
    """Make request to Notion API"""
    if not NOTION_API_KEY:
        raise HTTPException(status_code=503, detail="Notion API key not configured")
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json"
    }
    
    url = f"https://api.notion.com/v1/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code not in [200, 201]:
            logger.error(f"Notion API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        return response.json()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_healthy = False
    try:
        engine.connect()
        db_healthy = True
    except:
        pass
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "templatelinc",
        "oid": "1.3.6.1.4.1.61026.6.1",
        "version": "1.0.0",
        "notion_configured": bool(NOTION_API_KEY),
        "database": "connected" if db_healthy else "disconnected"
    }

@app.post("/api/v1/templates/sync")
async def sync_templates(sync_req: SyncRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Sync templates from Notion database"""
    if not NOTION_DATABASE_ID:
        raise HTTPException(status_code=503, detail="Notion database ID not configured")
    
    try:
        # Query Notion database
        query_data = {
            "page_size": 100
        }
        
        result = await notion_request("POST", f"databases/{NOTION_DATABASE_ID}/query", query_data)
        
        synced_count = 0
        for page in result.get("results", []):
            # Extract template data from Notion page
            template_id = page["id"]
            properties = page.get("properties", {})
            
            # Extract title
            title_prop = properties.get("Name", {}).get("title", [])
            title = title_prop[0]["plain_text"] if title_prop else "Untitled"
            
            # Extract category
            category_prop = properties.get("Category", {})
            category = category_prop.get("select", {}).get("name", "general") if category_prop else "general"
            
            # Extract tags
            tags_prop = properties.get("Tags", {}).get("multi_select", [])
            tags = [tag["name"] for tag in tags_prop]
            
            # Check if template exists
            existing = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
            
            if existing:
                # Update existing
                existing.title = title
                existing.category = category
                existing.tags = tags
                existing.updated_at = datetime.utcnow()
            else:
                # Create new
                template_model = TemplateModel(
                    id=template_id,
                    title=title,
                    content="",  # Would need to fetch page content separately
                    category=category,
                    tags=tags,
                    metadata={"notion_id": template_id},
                    created_at=datetime.fromisoformat(page["created_time"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(page["last_edited_time"].replace("Z", "+00:00"))
                )
                db.add(template_model)
            
            synced_count += 1
        
        db.commit()
        logger.info(f"Synced {synced_count} templates from Notion")
        
        return {
            "status": "success",
            "synced": synced_count,
            "total": db.query(TemplateModel).count()
        }
        
    except Exception as e:
        logger.error(f"Sync failed: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@app.get("/api/v1/templates")
async def list_templates(category: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    """List all templates"""
    query = db.query(TemplateModel)
    
    if category:
        query = query.filter(TemplateModel.category == category)
    
    templates = query.limit(limit).all()
    
    return {
        "total": db.query(TemplateModel).count(),
        "templates": [Template(
            id=t.id,
            title=t.title,
            content=t.content,
            category=t.category,
            tags=t.tags or [],
            metadata=t.metadata or {},
            created_at=t.created_at,
            updated_at=t.updated_at
        ) for t in templates]
    }

@app.get("/api/v1/templates/{template_id}")
async def get_template(template_id: str, db: Session = Depends(get_db)):
    """Get a specific template by ID"""
    # Check cache first
    cached = get_cached_template(template_id)
    if cached:
        return cached
    
    template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    result = Template(
        id=template.id,
        title=template.title,
        content=template.content,
        category=template.category,
        tags=template.tags or [],
        metadata=template.metadata or {},
        created_at=template.created_at,
        updated_at=template.updated_at
    )
    
    # Cache the result
    cache_template(template_id, result)
    
    return result

@app.post("/api/v1/templates/search")
async def search_templates(query: TemplateQuery, db: Session = Depends(get_db)):
    """Search templates by query, category, or tags"""
    db_query = db.query(TemplateModel)
    
    # Filter by category
    if query.category:
        db_query = db_query.filter(TemplateModel.category == query.category)
    
    # Filter by tags
    if query.tags:
        for tag in query.tags:
            db_query = db_query.filter(TemplateModel.tags.contains([tag]))
    
    # Simple text search in title and content
    if query.query:
        search_term = f"%{query.query.lower()}%"
        db_query = db_query.filter(
            (TemplateModel.title.ilike(search_term)) | (TemplateModel.content.ilike(search_term))
        )
    
    results = db_query.limit(query.limit).all()
    
    return {
        "total": len(results),
        "query": query.query,
        "results": [Template(
            id=t.id,
            title=t.title,
            content=t.content,
            category=t.category,
            tags=t.tags or [],
            metadata=t.metadata or {},
            created_at=t.created_at,
            updated_at=t.updated_at
        ) for t in results]
    }

@app.post("/api/v1/templates")
async def create_template(template: Template, db: Session = Depends(get_db)):
    """Create a new template (and optionally sync to Notion)"""
    template_id = f"tpl_{int(datetime.utcnow().timestamp())}"
    
    template_model = TemplateModel(
        id=template_id,
        title=template.title,
        content=template.content,
        category=template.category,
        tags=template.tags,
        metadata=template.metadata,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(template_model)
    db.commit()
    db.refresh(template_model)
    
    logger.info(f"Created template: {template_id} - {template.title}")
    
    result = Template(
        id=template_model.id,
        title=template_model.title,
        content=template_model.content,
        category=template_model.category,
        tags=template_model.tags or [],
        metadata=template_model.metadata or {},
        created_at=template_model.created_at,
        updated_at=template_model.updated_at
    )
    
    return {
        "status": "created",
        "template": result
    }

@app.put("/api/v1/templates/{template_id}")
async def update_template(template_id: str, template: Template, db: Session = Depends(get_db)):
    """Update an existing template"""
    db_template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db_template.title = template.title
    db_template.content = template.content
    db_template.category = template.category
    db_template.tags = template.tags
    db_template.metadata = template.metadata
    db_template.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_template)
    
    # Invalidate cache
    try:
        redis_client.delete(f"template:{template_id}")
    except:
        pass
    
    logger.info(f"Updated template: {template_id}")
    
    result = Template(
        id=db_template.id,
        title=db_template.title,
        content=db_template.content,
        category=db_template.category,
        tags=db_template.tags or [],
        metadata=db_template.metadata or {},
        created_at=db_template.created_at,
        updated_at=db_template.updated_at
    )
    
    return {
        "status": "updated",
        "template": result
    }

@app.delete("/api/v1/templates/{template_id}")
async def delete_template(template_id: str, db: Session = Depends(get_db)):
    """Delete a template"""
    db_template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(db_template)
    db.commit()
    
    # Invalidate cache
    try:
        redis_client.delete(f"template:{template_id}")
    except:
        pass
    
    logger.info(f"Deleted template: {template_id}")
    
    return {"status": "deleted", "id": template_id}

@app.post("/api/v1/templates/{template_id}/analyze")
async def analyze_template(template_id: str, db: Session = Depends(get_db)):
    """Analyze template usage and metrics"""
    template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Perform analysis (placeholder - would integrate with AI in production)
    analysis = {
        "template_id": template_id,
        "title": template.title,
        "category": template.category,
        "tags": template.tags or [],
        "word_count": len(template.content.split()),
        "character_count": len(template.content),
        "readability_score": 75.0,  # Placeholder
        "sentiment": "neutral",
        "key_topics": (template.tags or [])[:3]
    }
    
    return analysis

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
