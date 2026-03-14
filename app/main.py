import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.models import ChatRequest, ChatResponse
from app.router import classify_intent, route_and_respond

app = FastAPI(title="LLM-Powered Prompt Router")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Step 1: Classify Intent
    intent_data = await classify_intent(request.message)
    
    # Step 2: Route and Respond
    result = await route_and_respond(request.message, intent_data)
    
    return result

@app.get("/health")
async def health():
    return {"status": "ok"}
