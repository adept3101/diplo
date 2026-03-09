from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Mapped, MappedColumn
from app.core.db import Base
from datetime import datetime

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    login = Column(String)
    password: Mapped[str] = MappedColumn()
    date_reg = Column(DateTime(timezone=True), default=datetime.utcnow)
