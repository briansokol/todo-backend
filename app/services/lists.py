from sqlalchemy.orm import Session
from app.models.todo_list import TodoList
from app.schemas.todo_list import TodoListCreate
from fastapi import HTTPException


def get_lists(db: Session):
    return db.query(TodoList).order_by(TodoList.created_at).all()


def get_list(db: Session, list_id: int) -> TodoList:
    todo_list = db.query(TodoList).filter(TodoList.id == list_id).first()
    if not todo_list:
        raise HTTPException(status_code=404, detail="List not found")
    return todo_list


def create_list(db: Session, data: TodoListCreate) -> TodoList:
    todo_list = TodoList(**data.model_dump())
    db.add(todo_list)
    db.commit()
    db.refresh(todo_list)
    return todo_list


def update_list(db: Session, list_id: int, data: TodoListCreate) -> TodoList:
    todo_list = get_list(db, list_id)
    for key, value in data.model_dump().items():
        setattr(todo_list, key, value)
    db.commit()
    db.refresh(todo_list)
    return todo_list


def delete_list(db: Session, list_id: int) -> None:
    todo_list = get_list(db, list_id)
    db.delete(todo_list)
    db.commit()
