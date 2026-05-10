from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.todo_list import TodoListCreate, TodoListOut
from app.services import lists as list_service

router = APIRouter(prefix="/lists", tags=["lists"])


@router.get("", response_model=List[TodoListOut])
def get_lists(db: Session = Depends(get_db)):
    return list_service.get_lists(db)


@router.post("", response_model=TodoListOut, status_code=201)
def create_list(data: TodoListCreate, db: Session = Depends(get_db)):
    return list_service.create_list(db, data)


@router.get("/{list_id}", response_model=TodoListOut)
def get_list(list_id: int, db: Session = Depends(get_db)):
    return list_service.get_list(db, list_id)


@router.put("/{list_id}", response_model=TodoListOut)
def update_list(list_id: int, data: TodoListCreate, db: Session = Depends(get_db)):
    return list_service.update_list(db, list_id, data)


@router.delete("/{list_id}", status_code=204)
def delete_list(list_id: int, db: Session = Depends(get_db)):
    list_service.delete_list(db, list_id)
