from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.tag import Tag
from app.models.todo import Todo
from app.schemas.todo import TagCreate


def get_tags(db: Session) -> list[Tag]:
    """Return all Tag rows."""
    return db.query(Tag).all()


def create_tag(db: Session, data: TagCreate) -> Tag:
    """Create a new tag. Raises HTTPException(409) if name already exists."""
    tag = Tag(name=data.name, color=data.color)
    db.add(tag)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tag name already exists")
    db.refresh(tag)
    return tag


def add_tag_to_todo(db: Session, todo_id: int, tag_id: int) -> None:
    """Link a tag to a todo. Raises HTTPException(404) if todo or tag not found."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag not in todo.tags:
        todo.tags.append(tag)
        db.commit()


def remove_tag_from_todo(db: Session, todo_id: int, tag_id: int) -> None:
    """Unlink a tag from a todo. Raises HTTPException(404) if todo or tag not found."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag in todo.tags:
        todo.tags.remove(tag)
        db.commit()
