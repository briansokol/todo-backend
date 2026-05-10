from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.todo import Priority, Status
from app.schemas.todo import TodoCreate, TodoUpdate, TodoOut
from app.services import todos as todo_service
from app.services import lists as list_service

router = APIRouter(tags=["todos"])


@router.get("/lists/{list_id}/todos", response_model=List[TodoOut])
def get_todos(
    list_id: int,
    priority: Optional[Priority] = Query(None),
    status: Optional[Status] = Query(None),
    due_before: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    list_service.get_list(db, list_id)  # raises 404 if list not found
    return todo_service.get_todos(db, list_id, priority, status, due_before)


@router.post("/lists/{list_id}/todos", response_model=TodoOut, status_code=201)
def create_todo(list_id: int, data: TodoCreate, db: Session = Depends(get_db)):
    list_service.get_list(db, list_id)
    return todo_service.create_todo(db, list_id, data)


@router.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    return todo_service.get_todo(db, todo_id)


@router.put("/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, data: TodoUpdate, db: Session = Depends(get_db)):
    return todo_service.update_todo(db, todo_id, data)


@router.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_service.delete_todo(db, todo_id)
