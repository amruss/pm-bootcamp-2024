"""
Excuse Email Draft Tool - FastAPI Backend
A complete web application for generating excuse emails using Databricks Model Serving LLM.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Excuse Email Draft Tool",
    description="Generate professional excuse emails using AI",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment configuration
DATABRICKS_API_TOKEN = os.getenv("DATABRICKS_API_TOKEN")
DATABRICKS_ENDPOINT_URL = os.getenv(
    "DATABRICKS_ENDPOINT_URL", 
    "https://dbc-32cf6ae7-cf82.staging.cloud.databricks.com/serving-endpoints/databricks-gpt-oss-120b/invocations"
)
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# Request/Response Models
class ExcuseRequest(BaseModel):
    category: str
    tone: str
    seriousness: int
    recipient_name: str
    sender_name: str
    eta_when: str

class ExcuseResponse(BaseModel):
    subject: str
    body: str
    success: bool
    error: Optional[str] = None

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# Health check endpoints
@app.get("/health")
@app.get("/healthz")
@app.get("/ready")
@app.get("/ping")
async def health_check():
    """Health check endpoints for monitoring"""
    return {"status": "healthy", "service": "excuse-email-tool"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return {
        "service": "excuse-email-tool",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/debug")
async def debug():
    """Debug endpoint for environment information"""
    return {
        "environment": {
            "DATABRICKS_API_TOKEN": "***" if DATABRICKS_API_TOKEN else "Not set",
            "DATABRICKS_ENDPOINT_URL": DATABRICKS_ENDPOINT_URL,
            "PORT": PORT,
            "HOST": HOST
        },
        "paths": {
            "current_dir": os.getcwd(),
            "public_dir": str(Path("public").absolute()),
            "index_html": str(Path("public/index.html").absolute())
        }
    }

# Main API endpoint
@app.post("/api/generate-excuse", response_model=ExcuseResponse)
async def generate_excuse(request: ExcuseRequest):
    """Generate an excuse email using Databricks Model Serving LLM"""
    try:
        logger.info(f"Generating excuse for: {request.category} - {request.tone}")
        
        # Validate inputs
        if not request.recipient_name or not request.sender_name:
            raise HTTPException(status_code=400, detail="Recipient name and sender name are required")
        
        if request.seriousness < 1 or request.seriousness > 5:
            raise HTTPException(status_code=400, detail="Seriousness must be between 1 and 5")
        
        # Create the prompt for the LLM
        prompt = create_excuse_prompt(request)
        
        # Call Databricks Model Serving
        llm_response = await call_databricks_llm(prompt)
        
        # Parse the response
        parsed_response = parse_llm_response(llm_response, request)
        
        return ExcuseResponse(
            subject=parsed_response["subject"],
            body=parsed_response["body"],
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error generating excuse: {str(e)}")
        return ExcuseResponse(
            subject="",
            body="",
            success=False,
            error=str(e)
        )

def create_excuse_prompt(request: ExcuseRequest) -> str:
    """Create a structured prompt for the LLM"""
    
    # Map seriousness to descriptive text
    seriousness_map = {
        1: "very silly and humorous",
        2: "light and playful", 
        3: "balanced and professional",
        4: "serious and formal",
        5: "very serious and professional"
    }
    
    seriousness_desc = seriousness_map.get(request.seriousness, "balanced")
    
    prompt = f"""
You are an expert email writer. Generate a professional excuse email based on the following requirements:

Category: {request.category}
Tone: {request.tone}
Seriousness Level: {seriousness_desc} (scale 1-5, current: {request.seriousness})
Recipient: {request.recipient_name}
Sender: {request.sender_name}
ETA/When: {request.eta_when}

Please generate a JSON response with the following structure:
{{
    "subject": "Appropriate email subject line",
    "body": "Complete email body with greeting, apology, reason, next steps, and sign-off"
}}

Requirements:
- The email should be appropriate for the {request.tone} tone
- Match the {seriousness_desc} seriousness level
- Include the specific ETA/when information: {request.eta_when}
- Address {request.recipient_name} appropriately
- Sign off from {request.sender_name}
- Keep it professional but match the requested tone
- The body should be well-formatted with proper paragraphs

Return only the JSON response, no additional text.
"""
    
    return prompt.strip()

async def call_databricks_llm(prompt: str) -> str:
    """Call the Databricks Model Serving LLM"""
    
    if not DATABRICKS_API_TOKEN:
        raise HTTPException(status_code=500, detail="DATABRICKS_API_TOKEN not configured")
    
    headers = {
        "Authorization": f"Bearer {DATABRICKS_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                DATABRICKS_ENDPOINT_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"LLM Response: {result}")
            
            # Handle different response formats
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            elif "predictions" in result and len(result["predictions"]) > 0:
                return result["predictions"][0]
            elif "content" in result:
                return result["content"]
            else:
                return str(result)
                
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error calling Databricks LLM: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=500, detail=f"LLM service error: {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Request error calling Databricks LLM: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to connect to LLM service")
    except Exception as e:
        logger.error(f"Unexpected error calling Databricks LLM: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error calling LLM service")

def parse_llm_response(response: str, request: ExcuseRequest) -> Dict[str, str]:
    """Parse the LLM response and extract subject and body"""
    
    try:
        # Try to parse as JSON first
        if response.strip().startswith('{'):
            data = json.loads(response.strip())
            return {
                "subject": data.get("subject", f"Re: {request.category}"),
                "body": data.get("body", "Email content could not be generated.")
            }
    except json.JSONDecodeError:
        pass
    
    # Fallback: try to extract from text response
    lines = response.strip().split('\n')
    subject = f"Re: {request.category}"
    body = response.strip()
    
    # Look for subject line patterns
    for line in lines:
        if line.lower().startswith('subject:'):
            subject = line.split(':', 1)[1].strip()
            break
        elif line.lower().startswith('subject'):
            subject = line.split(' ', 1)[1].strip() if ' ' in line else f"Re: {request.category}"
            break
    
    # Clean up the body
    body_lines = []
    skip_subject = False
    
    for line in lines:
        if line.lower().startswith(('subject:', 'subject ')):
            skip_subject = True
            continue
        if not skip_subject or line.strip():
            body_lines.append(line)
    
    body = '\n'.join(body_lines).strip()
    
    # If body is empty or too short, create a fallback
    if not body or len(body) < 50:
        body = f"""Dear {request.recipient_name},

I wanted to let you know that I'm running late due to {request.category.lower()}.

{request.eta_when}

I apologize for any inconvenience this may cause.

Best regards,
{request.sender_name}"""
    
    return {
        "subject": subject,
        "body": body
    }

# Static file serving for React app
def get_static_file_path(filename: str) -> Optional[Path]:
    """Get the path to a static file, trying multiple locations"""
    possible_paths = [
        Path(filename),
        Path("public") / filename,
        Path(".") / "public" / filename,
        Path("/app/public") / filename,
        Path("/app") / filename
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Found static file: {path.absolute()}")
            return path
    
    logger.warning(f"Static file not found: {filename}")
    return None

@app.get("/")
async def serve_react_app():
    """Serve the React application"""
    index_path = get_static_file_path("index.html")
    
    if not index_path:
        return HTMLResponse("""
        <html>
            <head><title>Excuse Email Tool</title></head>
            <body>
                <h1>Excuse Email Draft Tool</h1>
                <p>React app not found. Please ensure index.html is in the public/ directory.</p>
                <p>Current working directory: {}</p>
            </body>
        </html>
        """.format(os.getcwd()), status_code=404)
    
    return FileResponse(index_path)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="public"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
