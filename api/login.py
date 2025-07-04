import os
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import pyotp
from cachetools import TTLCache
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import jwt
import datetime

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
import re

from models import get_db
from models.user import DbUser

load_dotenv()

otps = TTLCache(maxsize=1000, ttl=300)

router = APIRouter()

EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL = os.getenv("EMAIL")
SECRET_KEY = os.getenv("SECRET_KEY")


class LoginRequest(BaseModel):
    email: str


class OTPVerificationRequest(BaseModel):
    email: str
    otp: str


def send_email(to_address, subject, message):
    s = smtplib.SMTP(host="smtp.gmail.com", port=587)
    s.starttls()
    assert EMAIL is not None
    assert EMAIL_PASSWORD is not None
    s.login(EMAIL, EMAIL_PASSWORD)

    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(message))

    s.send_message(msg)
    s.quit()


@router.post("/login")
async def login(request: LoginRequest):
    pattern = r"f20(19|20|21|22|23|24)\d{4}@hyderabad.bits-pilani.ac.in$"

    if not re.match(pattern, request.email):
        return {"error": "Invalid e-mail id"}

    totp = pyotp.TOTP(pyotp.random_base32())
    otp = totp.now()
    while otp in otps.values():
        totp = pyotp.TOTP(pyotp.random_base32())
        otp = totp.now()
    otps[request.email] = otp
    send_email(
        request.email,
        "Terminal Arcade Login OTP",
        f"Your otp for login to Terminal Arcade is {otp}",
    )

    return {"message": "OTP sent"}


@router.post("/verify-otp")
async def verify(
    request: OTPVerificationRequest, db: Annotated[AsyncSession, Depends(get_db)]
):
    actual_otp = otps.get(request.email)
    if actual_otp is None or actual_otp != request.otp:
        return {"error": "Invalid OTP"}

    payload = {
        "sub": request.email,
        "iat": datetime.datetime.now(datetime.UTC),
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1),
    }
    assert SECRET_KEY is not None
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    user = await db.get(DbUser, request.email)
    if user is None:
        qry = insert(DbUser).values(email=request.email)
        await db.execute(qry)

    return {"access_token": token, "token_type": "bearer"}
