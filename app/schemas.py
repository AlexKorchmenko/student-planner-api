from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import enum


class EventCreate(BaseModel):
    title: str
    date: datetime
    user_id: int


class EventOut(BaseModel):
    id: int
    title: str
    date: datetime
    user_id: int

    class Config:
        from_attributes = True


# Tasks
class TaskCreate(BaseModel):
    title: str
    deadline: datetime
    priority: Optional[str]
    is_done: Optional[bool] = False
    user_id: int


class Task(BaseModel):
    id: int
    title: str
    deadline: datetime
    priority: Optional[str]
    is_done: Optional[bool]
    user_id: int

    class Config:
        from_attributes = True
class UserRole(str, enum.Enum):
    guest = "guest"
    student = "student"
    admin = "admin"

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.student

class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str

    class Config:
       from_attributes=True


class TaskUpdate(BaseModel):
    title: str
    date: datetime
    priority: str
    is_done: bool

class TaskOut(BaseModel):
    id: int
    title: str
    deadline: datetime
    priority: str
    is_done: bool
    user_id: int

    class Config:
        orm_mode = True

class AnalysisResult(BaseModel):
    recommendations: List[str]