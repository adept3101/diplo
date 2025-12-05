from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, Mapped, MappedColumn
from app.core.db import Base

# Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    login = Column(String)
    # password = Column(String)
    password: Mapped[str] = MappedColumn()
