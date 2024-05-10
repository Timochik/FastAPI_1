from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from starlette import status
from main import ContactInDB, ContactCreate
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from .models import Contact
from dotenv import dotenv_values


SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:567234@localhost:5432/fastdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = 'secret_key'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl = '/login' )

class CreateUserRequest(BaseModel):
    """
    Represents user data for creating a new user.

    Attributes:
        username (str): The username for the new user.
        password (str): The password for the new user.
    """
    username: str
    password: str

class Token(BaseModel):
    """
    Represents the access token information.

    Attributes:
        access_token (str): The generated access token string.
        token_type (str): The type of token (usually 'bearer' for bearer token authentication).
    """
    access_token: str
    token_type: str

def get_db():
    """Creates a database session and yields it for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

    
db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", status_code = status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    """
    Creates a new user in the database.

    Args:
        db: The database dependency to interact with the database.
        create_user_request: A pydantic model containing the username and password
                             for the new user.

    Returns:
        The newly created user object (ContactCreate) on success.

    Raises:
        HTTPException: If there is an error creating the user.
    """
    create_user_model = ContactCreate(
        username = create_user_request.username,
        hashed_password = bcrypt_context.hash(create_user_request.password),
    )

    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model= Token)
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                             db: db_dependency):
        """
    Generates an access token for a user who successfully logs in.

    Args:
        form_data: An annotated OAuth2PasswordRequestForm model containing the
                   username and password for authentication.
        db: The database dependency to interact with the database.

    Returns:
        A dictionary containing the access token and token type ('bearer').

    Raises:
        HTTPException: If the username or password is invalid.
    """
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail = 'Could not validate user.')
        token = create_access_token(user.username, user.id,timedelta(minutes=20))

        return {'access_token': token, 'token_type': 'bearer'}

def authenticate_user(username: str, password: str, db):
     """
    Authenticates a user by checking their username and password against the database.

    Args:
        username: The username of the user to authenticate.
        password: The password of the user to authenticate.
        db: The database session to query users.

    Returns:
        The user object if authentication is successful, otherwise None.
    """
     user = db.query(ContactInDB).filter(ContactInDB.username == username).first()
     if not user:
          return False
     if not bcrypt_context.verify(password, user.hashed_password):
          return False
     return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
     """
    Creates a JSON Web Token (JWT) for access control.

    Args:
        username: The username of the user for whom the token is generated.
        user_id: The ID of the user for whom the token is generated.
        expires_delta: A timedelta object specifying the token's expiration time.

    Returns:
        The encoded JWT string.
    """
     encode = {'sub': username, 'id': user_id}
     expires = datetime.now() + expires_delta
     encode.update({'exp': expires})
     return jwt.encode(encode, SECRET_KEY, algorithm = ALGORITHM)

async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
    """
    Retrieves the user information from a valid access token.

    Args:
        token: The access token to decode and extract user information.

    Returns:
        A dictionary containing the user's username and ID.

    Raises:
        HTTPException
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail = 'Could not validate user.')
        return {'username': username, 'id': user_id}
    except JWTError:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail = 'Could not validate user.')

async def get_user_by_email(db: Session, email: str) -> Contact | None:
     return db.query(Contact).filter(Contact).first()

    
async def confirmed_email(email: str, db: Session) -> None:
    user = await get_current_user(email, db)
    user.confirmed = True
    db.commit()

config_credential = dotenv_values(".env")

async def very_token(token: str):
    try:
        payload = jwt.decode(token, config_credential['SECRET'], algorithms=['HS256'])
        user = await Contact.get(id = payload.get("id"))

    except:
         raise HTTPException(
              status_code = status.HTTP_401_UNAUTHORIZED,
              detail = "Invalid token",
              headers = {"WWW-Authenticate": "Bearer"}
         )
    return user
    