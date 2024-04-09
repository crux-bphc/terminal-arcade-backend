import os
from fastapi import Request, Response
from typing import Callable
import jwt
from dotenv import load_dotenv
import json

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

async def auth_middleware(request: Request, call_next: Callable):
    try:
        if request.url.path not in ("/login", "/verify-otp"):
            token = request.cookies.get("token")
            payload = jwt.decode(token, SECRET_KEY, algorithms = ['HS256'])
            email = payload.get('sub')
            if email is None:
                return Response(content = json.dumps({"detail": "Invalid authentication credentials"}), status_code = 401)
    except Exception as e:
        return Response(content = json.dumps({"detail": "Invalid authentication credentials"}), status_code = 401)
    return await call_next(request)