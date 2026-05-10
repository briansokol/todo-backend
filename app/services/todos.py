from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.models.todo import Todo, Priority, Status
from app.schemas.todo import TodoCreate, TodoUpdate
from fastapi import HTTPException


def get_todos(
    db: Session,
    list_id: int,
    priority: Optional[Priority] = None,
    status: Optional[Status] = None,
    due_before: Optional[date] = None,
):
    query = db.query(Todo).filter(Todo.list_id == list_id)
    if priority is not None:
        query = query.filter(Todo.priority == priority)
    if status is not None:
        query = query.filter(Todo.status == status)
    if due_before is not None:
        query = query.filter(Todo.due_date <= due_before)
    return query.order_by(Todo.created_at).all()


def get_todo(db: Session, todo_id: int) -> Todo:
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


def create_todo(db: Session, list_id: int, data: TodoCreate) -> Todo:
    todo = Todo(list_id=list_id, **data.model_dump())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def update_todo(db: Session, todo_id: int, data: TodoUpdate) -> Todo:
    todo = get_todo(db, todo_id)
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, todo_id: int) -> None:
    todo = get_todo(db, todo_id)
    db.delete(todo)
    db.commit()
