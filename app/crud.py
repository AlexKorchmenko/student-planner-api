from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_users(db: Session):
    return db.query(models.User).all()

def create_user(db: Session, user: schemas.UserCreate):
    try:
        hashed_password = pwd_context.hash(user.password)
        db_user = models.User(
            email=user.email,
            full_name=user.full_name,
            password_hash=hashed_password,
            role="student"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        print("❌ Error creating user:", e)
        raise

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user and pwd_context.verify(password, user.password_hash):
        return user
    return None

def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_events_by_user(db: Session, user_id: int):
    return db.query(models.Event).filter(models.Event.user_id == user_id).all()

def update_event(db: Session, event_id: int, updated_data: dict):
    event = db.query(models.Event).get(event_id)
    for key, value in updated_data.items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event

def delete_event(db: Session, event_id: int):
    event = db.query(models.Event).get(event_id)
    db.delete(event)
    db.commit()

def create_task(db: Session, task: schemas.TaskCreate):
    task_data = task.dict()
    if isinstance(task_data["deadline"], datetime) and task_data["deadline"].tzinfo is not None:
        task_data["deadline"] = task_data["deadline"].replace(tzinfo=None)

    db_task = models.Task(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks_by_user(db: Session, user_id: int):
    return db.query(models.Task).filter(models.Task.user_id == user_id).all()

def update_task(db: Session, task_id: int, task_data: schemas.TaskUpdate):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        task.title = task_data.title
        task.date = task_data.date
        task.priority = task_data.priority
        task.is_done = task_data.is_done
        db.commit()
        db.refresh(task)
        return task
    return None

def delete_task(db: Session, task_id: int):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return True
    return False

