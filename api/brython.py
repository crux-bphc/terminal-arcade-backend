from string import ascii_lowercase, digits
from random import choices
import asyncio

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import PlainTextResponse

router = APIRouter()


class Hanger:
    def __init__(self):
        self.store = {}

    def generate_key(self):
        while True:
            key = "".join(choices(ascii_lowercase + digits, k=16))
            if key not in self.store:
                return key


handler = Hanger()


@router.get("/hanger/sleep/{duration}/", response_class=PlainTextResponse)
async def handle_sleep(duration: float):
    try:
        duration = min(duration, 60)
        await asyncio.sleep(duration)
        return f"{duration:.2f}"
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        return "-1"


@router.post("/hanger/open/", response_class=PlainTextResponse)
async def handle_open_slot():
    key = handler.generate_key()
    handler.store[key] = None
    return key


@router.post("/hanger/{key}/write/", response_class=PlainTextResponse)
async def handle_write_slot(
    key: str,
    data: str = Body(...),
):
    if key not in handler.store:
        raise HTTPException(status_code=404, detail="Key not found")

    handler.store[key] = data
    return key


@router.post("/hanger/{key}/read/", response_class=PlainTextResponse)
async def handle_read_slot(key: str):
    while True:
        if key in handler.store:
            if handler.store[key] is None:
                await asyncio.sleep(1)
            else:
                return handler.store.pop(key)
        else:
            raise HTTPException(status_code=404, detail="Key not found")
