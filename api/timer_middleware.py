import os
from fastapi import Request, Response
from typing import Callable
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

tz = ZoneInfo('Asia/Calcutta')
SECRET_KEY = os.getenv("SECRET_KEY")
start_time = datetime(2025, 4, 11, 21, 0, 0, 0,tzinfo=tz)

async def timer_middleware(request: Request, call_next: Callable):
    t = datetime.now(tz)
    time_left = start_time - t
    if time_left > timedelta(seconds=0):
        return Response(
            content=json.dumps(
                {"detail": f"event has not begun, {':'.join(str(time_left).split(':')[:2])} time left"}
            ),
        )

    return await call_next(request)

