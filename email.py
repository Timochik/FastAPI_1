from pathlib import Path
from fastapi import(BackgroundTasks, UploadFile, 
                    File, Form, Depends, HTTPException, status)
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from dotenv import dotenv_values
from pydantic import BaseModel, EmailStr
from typing import List
from .models import Contact
import jwt

from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from .auth import auth_service

config_credentials = dotenv_values(".env")

conf = ConnectionConfig(
    MAIL_USERNAME = config_credentials["EMAIL"],
    MAIL_PASSWORD = config_credentials["PASS"],
    MAIL_FROM = config_credentials["EMAIL"],
    MAIL_PORT= 507,
    MAIL_SERVER="smtp.gmail.com ",
    MAIL_FROM_NAME="Desired Name",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)



async def send_email(email: List, instance: Contact):
    token_data = {
        "id": instance.contact_id,
        "username": instance.first_name,
    }
    token = jwt.encode(token_data, config_credentials["Secret"], algorithm=['HS256'])

    template = f"""
        <!DOCTYPE html>
        <html>
            <head>

            </head>
            <body>
                <div style = "display: flex; align-items: center; justify-content: center; flex-direction: column">

                    <h3>Account Verification </hs>
                    <br>

                    <p> Thanks for choosing us, please click the button below to verify your account </p>

                    <a> style= "marign-top: 1rem; padding: 1rem; border-radius: 0.5rem;
                    front-size: 1rem; text-decoration: none; background: #0275d8; color: white;
                    " href="http://localhost:8000/verification/?token={token}">
                    Verify your email
                    </a>

                    <p>Please kindly ignore this email if you did not register for 
                    us and nothing will happen. Thanks</p>
                <div>
            </body>
        </html> 
    """
    
    
    message = MessageSchema(
        subject="Account Verification Email", 
        recipients= email, #List of recipients
        body= template,
        subtype= "html"
    )

    fm = FastMail(conf)
    await fm.send_message(message=message)

