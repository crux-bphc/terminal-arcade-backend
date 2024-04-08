import os
from fastapi import APIRouter
from pydantic import BaseModel
import pyotp
from cachetools import TTLCache
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import jwt
import datetime

load_dotenv()

otps = TTLCache(maxsize = 1000, ttl = 300)

router = APIRouter()

SECRET_KEY = os.getenv('SECRET_KEY')

class LoginRequest(BaseModel):
    email: str

class OTPVerificationRequest(BaseModel):
    email: str
    otp: str

def send_email(to_address, subject, message):
    from_address = os.getenv('EMAIL')
    s = smtplib.SMTP(host = 'smtp.gmail.com', port = 587)
    s.starttls()
    s.login(from_address, os.getenv('PASSWORD'))

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(message))

    s.send_message(msg)
    s.quit()

@router.post("/login")
async def login(request: LoginRequest):
    totp = pyotp.TOTP(pyotp.random_base32())
    otp = totp.now()
    while otp in otps.values():
        totp = pyotp.TOTP(pyotp.random_base32())
        otp = totp.now()
    otps[request.email] = otp
    send_email(request.email, "Terminal Arcade Login OTP", f"Your otp for login to Terminal Arcade is {otp}")

    return {"message": "OTP sent"}

@router.post("/verify-otp")
async def verify(request: OTPVerificationRequest):
    actual_otp = otps.get(request.email)
    if actual_otp and actual_otp == request.otp:
        payload = {
            'sub': request.email,
            'iat': datetime.datetime.now(datetime.UTC),
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days = 1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm = 'HS256')

        return {"access_token": token, "token_type": "bearer"}
    else:
        return {"error": "Invalid OTP"}






