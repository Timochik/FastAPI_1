# Imports required libraries for FastAPI, database interaction, and data validation
from fastapi import FastAPI, HTTPException, Depends, Request, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import List, Optional
from datetime import date, timedelta
from pydantic import BaseModel
from models import Contact
import auth
from auth import very_token

# Imports for templating and email
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from email import *

# Define database connection URL and create engine and session local object
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:567234@localhost:5432/fastdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create a FastAPI application instance and include the auth router
app = FastAPI()
app.include_router(auth.router)

# Health checker
@app.get("/healthcheck")
async def healthcheck():
    """Performs a basic health check on the application.

    Returns:
        dict: A dictionary containing a "status" key with the value "ok".
    """
    return {"status": "ok"}

# Клас моделі для Pydantic
class ContactInDB(BaseModel):
    """Represents a contact stored in the database.

    Attributes:
        contact_id (int): The unique identifier for the contact.
        first_name (str): The contact's first name.
        last_name (str): The contact's last name.
        email (str): The contact's email address.
        phone_number (str): The contact's phone number (optional).
        birthday (date): The contact's birthday (optional).
        additional_info (str): Any additional information about the contact (optional).
    """
    
    contact_id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: Optional[date] 
    additional_info: Optional[str]

class ContactCreate(BaseModel):
    """Represents data required to create a new contact.

    Attributes:
        first_name (str): The contact's first name.
        last_name (str): The contact's last name.
        email (str): The contact's email address.
        phone_number (str): The contact's phone number (optional).
        birthday (date): The contact's birthday (optional).
        additional_info (str): Any additional information about the contact (optional).
    """
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: Optional[date] 
    additional_info: Optional[str]

class ContactUpdate(BaseModel):
    """Represents data for partially updating a contact.

    Attributes:
        first_name (str): The contact's first name (optional).
        last_name (str): The contact's last name (optional).
        email (str): The contact's email address (optional).
        phone_number (str): The contact's phone number (optional).
        birthday (date): The contact's birthday (optional).
        additional_info (str): Any additional information about the contact (optional).
    """
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    birthday: Optional[date]
    additional_info: Optional[str]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD операції
@app.post("/contacts/", response_model=ContactInDB)
async def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    """Creates a new contact in the database.

    Args:
        contact (ContactCreate): The contact data to be created.
        db (Session): The database session dependency.

    Returns:
        ContactInDB: The newly created contact details.

    Raises:
        HTTPException: If there is an error creating the contact.
    """
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

    return db_contact

@app.get("/contacts/", response_model=List[ContactInDB])
async def read_contacts(query: str = None, db: Session = Depends(get_db)):
    """Retrieves all contacts from the database.

    Args:
        query (str, optional): A search query to filter contacts by first name, last name, or email.
        db (Session): The database session dependency.

    Returns:
        List[ContactInDB]: A list of all contact details or filtered contacts based on the query.
    """
    if query:
        return db.query(ContactInDB).filter(
            (ContactInDB.first_name.ilike(f'%{query}%')) |
            (ContactInDB.last_name.ilike(f'%{query}%')) |
            (ContactInDB.email.ilike(f'%{query}%'))
        ).all()
    return db.query(ContactInDB).all()

@app.get("/contacts/{contact_id}", response_model=ContactInDB)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    """Retrieves a specific contact by its ID.

    Args:
        contact_id (int): The unique identifier of the contact.
        db (Session): The database session dependency.

    Returns:
        ContactInDB: The contact details for the requested ID.

    Raises:
        HTTPException: If the contact with the given ID is not found.
    """
    contact = db.query(ContactInDB).filter(ContactInDB.contact_id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=ContactInDB)
async def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)):
    """Updates an existing contact in the database.

    Args:
        contact_id (int): The unique identifier of the contact.
        contact (ContactUpdate): The updated contact data.
        db (Session): The database session dependency.

    Returns:
        ContactInDB: The updated contact details.

    Raises:
        HTTPException: If the contact with the given ID is not found.
    """
    db_contact = db.query(ContactInDB).filter(ContactInDB.contact_id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    for key, value in contact.dict().items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """Deletes a contact from the database.

    Args:
        contact_id (int): The unique identifier of the contact.
        db (Session): The database session dependency 
    """
    contact = db.query(ContactInDB).filter(ContactInDB.contact_id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"}

@app.get("/contacts/birthday/", response_model=List[ContactInDB])
async def upcoming_birthdays(db: Session = Depends(get_db)):
    """Retrieves a list of contacts with birthdays within the next 7 days.

    Args:
        db (Session): The database session dependency.

    Returns:
        List[ContactInDB]: A list of contact details for upcoming birthdays.
    """
    today = date.today()
    end_date = today + timedelta(days=7)
    return db.query(ContactInDB).filter(ContactInDB.birthday.between(today, end_date)).all()

templates = Jinja2Templates(directory = "templates")

@app.get("/verification", response_class=HTMLResponse)
async def email_verification(requesr: Request, token: str):
    """Verifies a user's email address using a token.

    Args:
        requesr (Request): The incoming request object.
        token (str): The verification token.

    Returns:
        HTMLResponse: A rendered verification template on successful verification.

    Raises:
        HTTPException: If the token is invalid or the user is already verified.
    """
    user = await very_token(token)

    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse("verification.html",
                                          {"request": Request, "username": user.first_name } )
    
    raise HTTPException(
              status_code = status.HTTP_401_UNAUTHORIZED,
              detail = "Invalid token",
              headers = {"WWW-Authenticate": "Bearer"}
         )

