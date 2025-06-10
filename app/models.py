from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, Boolean, ForeignKey, DateTime
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    guest = "guest"
    student = "student"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole), default="student")
    created_at = Column(TIMESTAMP)



class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=False)
    priority = Column(String)
    is_done = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))