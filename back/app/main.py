from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from back.api import course
from app.api import course
from app.auth import auth
from app.api import profile
from app.api import predict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # разрешаем все источники
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(course.router)
app.include_router(profile.router)
# app.include_router(predict.router)
