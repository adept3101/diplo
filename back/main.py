from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from back.api import course
from api import course
from auth import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # разрешаем все источники
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(course.router)
app.include_router(router.router)
