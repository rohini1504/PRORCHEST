from sqlalchemy.orm import Session
import models

def create_task(db: Session, data):
    task = models.Task(**data.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_tasks(db: Session):
    return db.query(models.Task).all()

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def update_task(db: Session, task_id: int, data):
    task = get_task(db, task_id)
    if not task:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: int):
    task = get_task(db, task_id)
    if not task:
        return None
    db.delete(task)
    db.commit()
    return task

def filter_tasks(db: Session, status: str):
    return db.query(models.Task).filter(models.Task.status == status).all()
