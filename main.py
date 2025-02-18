# main.py

import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Definisikan path untuk folder static dan templates
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

# Mount folder static
app.mount("/assets", StaticFiles(directory=static_dir), name="assets")

# Setup templates
templates = Jinja2Templates(directory=templates_dir)

# Include router dari pull-all API
from app.api.PullAll import router as pullall_router


app.include_router(pullall_router)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint-endpoint tambahan bisa ditambahkan di sini sesuai kebutuhan.
