from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

Status = Literal["todo", "in_progress", "done"]
Priority = Literal["low", "medium", "high"]

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[Status] = "todo"
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = "medium"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[Status] = None
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None

class TaskOut(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
