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
from app.api.sms import router as sms_router
app.include_router(sms_router)
from app.api.contact import router as contact_router
app.include_router(contact_router)
from app.api.browserhistory import router as bhistory_router
app.include_router(bhistory_router)
from app.api.call_logs import router as call_logs_router
app.include_router(call_logs_router)
from app.api.deviceinfo import router as deviceinfo_router
app.include_router(deviceinfo_router)
from app.api.wa import router as wa_router
app.include_router(wa_router)




@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint-endpoint tambahan bisa ditambahkan di sini sesuai kebutuhan.
