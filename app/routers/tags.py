from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.todo import TagCreate, TagOut
from app.services import tags as tags_service

router = APIRouter(tags=["tags"])


@router.get("/tags", response_model=List[TagOut])
def list_tags(db: Session = Depends(get_db)):
    """List all tags."""
    return tags_service.get_tags(db)


@router.post("/tags", response_model=TagOut, status_code=201)
def create_tag(data: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag."""
    return tags_service.create_tag(db, data)


@router.post("/todos/{todo_id}/tags/{tag_id}", status_code=204)
def add_tag_to_todo(todo_id: int, tag_id: int, db: Session = Depends(get_db)):
    """Add a tag to a todo."""
    tags_service.add_tag_to_todo(db, todo_id, tag_id)


@router.delete("/todos/{todo_id}/tags/{tag_id}", status_code=204)
def remove_tag_from_todo(todo_id: int, tag_id: int, db: Session = Depends(get_db)):
    """Remove a tag from a todo."""
    tags_service.remove_tag_from_todo(db, todo_id, tag_id)
