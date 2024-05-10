from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Contact(Base):
    """Represents a contact stored in a database using SQLAlchemy.

    Attributes:
        __tablename__ (str): The name of the database table for contacts ("contacts").
        contact_id (int): The unique identifier for the contact (primary key).
        first_name (str): The contact's first name.
        last_name (str): The contact's last name.
        email (str): The contact's email address.
        phone_number (str): The contact's phone number (optional).
        birthday (date): The contact's birthday (optional).
        additional_info (str): Any additional information about the contact (optional).
        is_verified (bool): A flag indicating if the contact's email has been verified (default: False).
    """
    __tablename__ = "contacts"

    contact_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone_number = Column(String)
    birthday = Column(Date, nullable=True)
    additional_info = Column(String, nullable=True)
    is_verified  = Column(bool, default=False)