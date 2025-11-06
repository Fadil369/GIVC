from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime
import asyncio
import aiohttp
import os
from enum import Enum

app = FastAPI(
    title="BrainSait Agentic Workflow Orchestrator",
    description="AI-powered content creation and publishing workflow system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
WORDPRESS_URL = os.getenv("WORDPRESS_URL", "http://host.docker.internal:8080")
MOODLE_URL = os.getenv("MOODLE_URL", "http://host.docker.internal:8081")
N8N_URL = os.getenv("N8N_URL", "http://n8n:5678")

# Models
class ContentType(str, Enum):
    COURSE = "course"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    VIDEO_SCRIPT = "video_script"

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ContentRequest(BaseModel):
    content_type: ContentType
    topic: str
    target_audience: str = "general"
    tone: str = "professional"
    length: str = "medium"
    keywords: List[str] = []
    additional_context: Optional[str] = None

class WorkflowTask(BaseModel):
    id: str
    content_type: ContentType
    status: WorkflowStatus
    topic: str
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict] = None

# In-memory storage (replace with database in production)
workflows: Dict[str, WorkflowTask] = {}

# Agent definitions
class Agent:
    def __init__(self, name: str, role: str, model: str = "llama3.2"):
        self.name = name
        self.role = role
        self.model = model
    
    async def execute(self, prompt: str) -> str:
        """Execute agent task using Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    return ""
        except Exception as e:
            print(f"Agent {self.name} error: {e}")
            return ""

# Initialize agents
research_agent = Agent("Research Agent", "Conducts research and gathers information")
content_writer = Agent("Content Writer", "Creates engaging content")
editor_agent = Agent("Editor Agent", "Reviews and improves content quality")
seo_agent = Agent("SEO Agent", "Optimizes content for search engines")
course_designer = Agent("Course Designer", "Designs educational course structures")
social_media_agent = Agent("Social Media Agent", "Creates social media content")

# Workflow orchestration
async def create_blog_post(topic: str, audience: str, tone: str, keywords: List[str]) -> Dict:
    """Multi-agent workflow for blog post creation"""
    
    # Step 1: Research
    research_prompt = f"""
    Research the following topic thoroughly: {topic}
    Target audience: {audience}
    Focus on: Latest trends, key concepts, practical applications
    Provide a comprehensive research summary with key points.
    """
    research = await research_agent.execute(research_prompt)
    
    # Step 2: Content creation
    content_prompt = f"""
    Based on this research:
    {research}
    
    Write a comprehensive blog post about: {topic}
    Target audience: {audience}
    Tone: {tone}
    Keywords to include: {', '.join(keywords)}
    
    Structure: Introduction, Main sections with subheadings, Conclusion
    Length: 1500-2000 words
    """
    draft = await content_writer.execute(content_prompt)
    
    # Step 3: Editing
    edit_prompt = f"""
    Review and improve this blog post:
    {draft}
    
    Focus on: Grammar, clarity, flow, engagement, accuracy
    Provide the edited version.
    """
    edited = await editor_agent.execute(edit_prompt)
    
    # Step 4: SEO optimization
    seo_prompt = f"""
    Optimize this content for SEO:
    {edited}
    
    Target keywords: {', '.join(keywords)}
    
    Provide:
    1. Optimized title
    2. Meta description
    3. Slug
    4. Suggested tags
    5. SEO-optimized content
    """
    seo_optimized = await seo_agent.execute(seo_prompt)
    
    return {
        "research": research,
        "draft": draft,
        "edited": edited,
        "seo_optimized": seo_optimized,
        "status": "completed"
    }

async def create_course(topic: str, audience: str, length: str) -> Dict:
    """Multi-agent workflow for course creation"""
    
    # Step 1: Course structure design
    structure_prompt = f"""
    Design a comprehensive online course structure for: {topic}
    Target audience: {audience}
    Course length: {length}
    
    Provide:
    1. Course title and description
    2. Learning objectives
    3. Module breakdown with topics
    4. Estimated duration per module
    5. Assessment strategy
    """
    structure = await course_designer.execute(structure_prompt)
    
    # Step 2: Content for each module
    modules_prompt = f"""
    Based on this course structure:
    {structure}
    
    Create detailed content for the first 3 modules including:
    1. Module overview
    2. Key concepts
    3. Learning activities
    4. Assessment questions
    """
    modules = await content_writer.execute(modules_prompt)
    
    # Step 3: Review and enhance
    review_prompt = f"""
    Review this course content:
    {modules}
    
    Enhance with:
    1. Interactive elements suggestions
    2. Real-world examples
    3. Additional resources
    """
    enhanced = await editor_agent.execute(review_prompt)
    
    return {
        "structure": structure,
        "modules": modules,
        "enhanced": enhanced,
        "status": "completed"
    }

async def create_social_posts(topic: str, tone: str) -> Dict:
    """Create social media content"""
    
    prompt = f"""
    Create engaging social media posts about: {topic}
    Tone: {tone}
    
    Generate:
    1. Twitter/X post (280 characters)
    2. LinkedIn post (professional, detailed)
    3. Instagram caption with hashtags
    4. Facebook post
    5. Thread starter for Twitter/X (3-5 tweets)
    
    Include relevant hashtags and call-to-actions.
    """
    social_content = await social_media_agent.execute(prompt)
    
    return {
        "social_posts": social_content,
        "status": "completed"
    }

async def process_workflow(workflow_id: str, request: ContentRequest):
    """Background task to process workflow"""
    workflows[workflow_id].status = WorkflowStatus.PROCESSING
    workflows[workflow_id].updated_at = datetime.now()
    
    try:
        if request.content_type == ContentType.BLOG_POST:
            result = await create_blog_post(
                request.topic,
                request.target_audience,
                request.tone,
                request.keywords
            )
        elif request.content_type == ContentType.COURSE:
            result = await create_course(
                request.topic,
                request.target_audience,
                request.length
            )
        elif request.content_type == ContentType.SOCIAL_POST:
            result = await create_social_posts(
                request.topic,
                request.tone
            )
        else:
            result = {"error": "Unsupported content type"}
        
        workflows[workflow_id].status = WorkflowStatus.COMPLETED
        workflows[workflow_id].result = result
    except Exception as e:
        workflows[workflow_id].status = WorkflowStatus.FAILED
        workflows[workflow_id].result = {"error": str(e)}
    
    workflows[workflow_id].updated_at = datetime.now()

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/workflow/create", response_model=WorkflowTask)
async def create_workflow(request: ContentRequest, background_tasks: BackgroundTasks):
    """Create a new content workflow"""
    import uuid
    
    workflow_id = str(uuid.uuid4())
    workflow = WorkflowTask(
        id=workflow_id,
        content_type=request.content_type,
        status=WorkflowStatus.PENDING,
        topic=request.topic,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    workflows[workflow_id] = workflow
    background_tasks.add_task(process_workflow, workflow_id, request)
    
    return workflow

@app.get("/workflow/{workflow_id}", response_model=WorkflowTask)
async def get_workflow(workflow_id: str):
    """Get workflow status and results"""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflows[workflow_id]

@app.get("/workflows", response_model=List[WorkflowTask])
async def list_workflows():
    """List all workflows"""
    return list(workflows.values())

@app.post("/publish/wordpress/{workflow_id}")
async def publish_to_wordpress(workflow_id: str):
    """Publish content to WordPress"""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    if workflow.status != WorkflowStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Workflow not completed")
    
    # TODO: Implement WordPress API integration
    return {"message": "Publishing to WordPress", "workflow_id": workflow_id}

@app.post("/publish/moodle/{workflow_id}")
async def publish_to_moodle(workflow_id: str):
    """Publish course to Moodle"""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    if workflow.status != WorkflowStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Workflow not completed")
    
    if workflow.content_type != ContentType.COURSE:
        raise HTTPException(status_code=400, detail="Only courses can be published to Moodle")
    
    # TODO: Implement Moodle API integration
    return {"message": "Publishing to Moodle", "workflow_id": workflow_id}

@app.get("/agents")
async def list_agents():
    """List available agents"""
    return {
        "agents": [
            {"name": "Research Agent", "role": "Information gathering and research"},
            {"name": "Content Writer", "role": "Content creation and writing"},
            {"name": "Editor Agent", "role": "Content review and improvement"},
            {"name": "SEO Agent", "role": "Search engine optimization"},
            {"name": "Course Designer", "role": "Educational course design"},
            {"name": "Social Media Agent", "role": "Social media content creation"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
