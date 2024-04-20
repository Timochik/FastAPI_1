from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import List, Optional
from datetime import date, timedelta
from pydantic import BaseModel
from models import Contact

# Підключення до бази даних
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:567234@localhost:5432/fastdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
app = FastAPI()

# Health checker
@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

# Клас моделі для Pydantic
class ContactInDB(BaseModel):
    contact_id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: Optional[date] 
    additional_info: Optional[str]

class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: Optional[date] 
    additional_info: Optional[str]

class ContactUpdate(BaseModel):
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
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.get("/contacts/", response_model=List[ContactInDB])
async def read_contacts(query: str = None, db: Session = Depends(get_db)):
    if query:
        return db.query(ContactInDB).filter(
            (ContactInDB.first_name.ilike(f'%{query}%')) |
            (ContactInDB.last_name.ilike(f'%{query}%')) |
            (ContactInDB.email.ilike(f'%{query}%'))
        ).all()
    return db.query(ContactInDB).all()

@app.get("/contacts/{contact_id}", response_model=ContactInDB)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(ContactInDB).filter(ContactInDB.contact_id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=ContactInDB)
async def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)):
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
    contact = db.query(ContactInDB).filter(ContactInDB.contact_id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"}

@app.get("/contacts/birthday/", response_model=List[ContactInDB])
async def upcoming_birthdays(db: Session = Depends(get_db)):
    today = date.today()
    end_date = today + timedelta(days=7)
    return db.query(ContactInDB).filter(ContactInDB.birthday.between(today, end_date)).all()