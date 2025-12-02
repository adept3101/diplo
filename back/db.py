import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")

DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

# engine = create_async_engine(DATABASE_URL, echo=True)
engine = create_engine(DATABASE_URL, echo=True)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# async_session = async_sessionmaker(engine, expire_on_commit=False)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

engine.connect()
# print(engine)


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()
