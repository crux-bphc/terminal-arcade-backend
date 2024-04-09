from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.middleware import auth_middleware
from api.games import router as games_router
from api.user import router as user_router
from api.login import router as login_router
from api.brython import router as brython_router

app = FastAPI()

origins = [
    "https://terminal-arcade.vercel.app/",
    "http://localhost:5173"  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games_router)
app.include_router(user_router)
app.include_router(login_router)
app.include_router(brython_router)

app.middleware("http")(lambda request, call_next: auth_middleware(request, call_next)) 

@app.get("/")
def read_root():
    return {"Hello": "world"}