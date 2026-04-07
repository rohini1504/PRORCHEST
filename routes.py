from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, services
from database import get_db

router = APIRouter()

@router.post("/tasks", response_model=schemas.TaskResponse)
def create(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return services.create_task(db, task)

@router.get("/tasks")
def list_all(db: Session = Depends(get_db)):
    return services.get_tasks(db)

@router.get("/tasks/{task_id}")
def get_one(task_id: int, db: Session = Depends(get_db)):
    task = services.get_task(db, task_id)
    if not task:
        raise HTTPException(404, "Not found")
    return task

@router.put("/tasks/{task_id}")
def update(task_id: int, data: schemas.TaskUpdate, db: Session = Depends(get_db)):
    updated = services.update_task(db, task_id, data)
    if not updated:
        raise HTTPException(404, "Not found")
    return updated

@router.delete("/tasks/{task_id}")
def delete(task_id: int, db: Session = Depends(get_db)):
    deleted = services.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(404, "Not found")
    return {"msg": "Deleted"}

@router.get("/tasks/status/{status}")
def filter_status(status: str, db: Session = Depends(get_db)):
    return services.filter_tasks(db, status)
