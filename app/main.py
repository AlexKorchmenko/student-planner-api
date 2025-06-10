from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app import models, schemas, crud, database
from fastapi import HTTPException
from app.analytics import analyze_user_activity

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users", response_model=list[schemas.UserOut])
def read_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.post("/login", response_model=schemas.UserResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    user = crud.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return schemas.UserResponse.from_orm(user)

# EVENT ROUTES
@app.post("/events/", response_model=schemas.EventOut)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.create_event(db, event)

@app.get("/events/{user_id}", response_model=list[schemas.EventOut])
def read_events(user_id: int, db: Session = Depends(get_db)):
    return crud.get_events_by_user(db, user_id)

@app.put("/events/{event_id}")
def update_event(event_id: int, updated: dict, db: Session = Depends(get_db)):
    return crud.update_event(db, event_id, updated)

@app.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    crud.delete_event(db, event_id)
    return {"ok": True}

# TASK ROUTES
@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)

@app.get("/tasks/{user_id}", response_model=list[schemas.Task])
def read_tasks(user_id: int, db: Session = Depends(get_db)):
    return crud.get_tasks_by_user(db, user_id)

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(database.get_db)):
    db_task = crud.update_task(db, task_id, task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted"}


@app.patch("/tasks/{task_id}/toggle", response_model=schemas.TaskOut)
def toggle_task_done(task_id: int, is_done: bool, db: Session = Depends(database.get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_done = is_done
    db.commit()
    db.refresh(task)
    return task

@app.get("/analytics/{user_id}")
def get_user_analytics(user_id: int, db: Session = Depends(get_db)):
    return {"summary": analyze_user_activity(user_id, db)}