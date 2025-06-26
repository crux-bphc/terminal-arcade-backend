from typing import Annotated
from fastapi import Response, Security
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials
import os
import jwt
import json

bearer_extract = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY")


def get_email(token: Annotated[HTTPAuthorizationCredentials, Security(bearer_extract)]):
    assert SECRET_KEY is not None
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            return Response(
                content=json.dumps({"detail": "Invalid authentication credentials"}),
                status_code=401,
            )
    except Exception:
        return Response(
            content=json.dumps({"detail": "Invalid authentication credentials"}),
            status_code=401,
        )

    return email
