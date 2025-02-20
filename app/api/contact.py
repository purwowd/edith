from fastapi import APIRouter, Request
from app.service.contact import get_contacts
from app.service.most_contacts import most_contacts
from app.service.searchcontact import search_contact
router = APIRouter()

@router.get("/contacts")
async def contacts_endpoint(request: Request):
    return get_contacts()

@router.get("/most-contacted")
async def most_contacts_endpoint (request: Request):
    return most_contacts()

@router.get("/search-contact")
async def search_contact_endpoint (request: Request):
    return search_contact()