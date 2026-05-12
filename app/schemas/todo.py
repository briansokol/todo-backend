from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.todo import Priority, Status


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")


class TagOut(BaseModel):
    id: int
    name: str
    color: str

    model_config = {"from_attributes": True}


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Priority = Priority.medium
    due_date: Optional[date] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    due_date: Optional[date] = None


class TodoOut(BaseModel):
    id: int
    list_id: int
    title: str
    description: Optional[str] = None
    status: Status
    priority: Priority
    due_date: Optional[date] = None
    created_at: datetime
    tags: List[TagOut] = []

    model_config = {"from_attributes": True}
