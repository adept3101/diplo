from fastapi import FastAPI

# from back.api import course
from api import course

app = FastAPI()

app.include_router(course.router)
