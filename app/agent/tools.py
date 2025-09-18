from langchain_core.tools import tool
from sqlalchemy.orm import Session
from fastapi import Depends
from .. import models, schemas
from ..database import get_db
from ..database import SessionLocal
from datetime import datetime
import dateutil.parser

# LangGraph Tools - they should return JSON serializable data
# Allowed values
VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"todo", "in_progress", "done"}

def parse_date(date_str: str) -> datetime | None:
    """Parse natural language date like 'Monday' or 'next Friday'."""
    try:
        return dateutil.parser.parse(date_str, fuzzy=True)
    except Exception as e:
        print(f"[WARN] Could not parse date: {date_str!r} → {e}")
        return None

@tool("create_task")
def create_task(title: str, description: str = None, priority: str = "medium", status: str = "todo", due_date: str = None) -> dict:
    """Create a new task with optional description, priority, status, and natural language due_date."""

    if priority not in VALID_PRIORITIES:
        return {"error": f"Invalid priority '{priority}'. Must be one of: {', '.join(VALID_PRIORITIES)}"}

    if status not in VALID_STATUSES:
        return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}"}

    parsed_due_date = parse_date(due_date) if due_date else None

    db: Session = SessionLocal()
    task = models.Task(
        title=title,
        description=description,
        priority=priority,
        status=status,
        due_date=parsed_due_date
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None
    }

@tool("update_task")
def update_task(task_id: int, title: str = None, description: str = None, status: str = None, priority: str = None, due_date: str = None) -> dict:
    """Update fields of a task by ID. Accepts natural language due_date."""

    db: Session = SessionLocal()
    task = db.query(models.Task).get(task_id)
    if not task:
        return {"error": f"Task {task_id} not found."}

    if priority:
        if priority not in VALID_PRIORITIES:
            return {"error": f"Invalid priority '{priority}'. Must be one of: {', '.join(VALID_PRIORITIES)}"}
        task.priority = priority

    if status:
        if status not in VALID_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}"}
        task.status = status

    if title:
        task.title = title
    if description:
        task.description = description
    if due_date:
        parsed_due_date = parse_date(due_date)
        if parsed_due_date:
            task.due_date = parsed_due_date
        else:
            return {"error": f"Could not understand due_date: '{due_date}'."}

    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None
    }

@tool("delete_task")
def delete_task(task_id: int) -> dict:
    """Delete a task by ID."""
    from ..database import SessionLocal
    db: Session = SessionLocal()
    task = db.query(models.Task).get(task_id)
    if not task:
        return {"error": "Task not found"}
    db.delete(task)
    db.commit()
    return {"deleted": task_id}


@tool("list_tasks")
def list_tasks() -> list:
    """Return all tasks."""
    from ..database import SessionLocal
    db: Session = SessionLocal()
    tasks = db.query(models.Task).all()
    return [{"id": t.id, "title": t.title, "status": t.status, "priority": t.priority} for t in tasks]


@tool("filter_tasks")
def filter_tasks(status: str = None, priority: str = None) -> list:
    """Filter tasks by status or priority."""
    from ..database import SessionLocal
    db: Session = SessionLocal()
    q = db.query(models.Task)
    if status:
        q = q.filter(models.Task.status == status)
    if priority:
        q = q.filter(models.Task.priority == priority)
    tasks = q.all()
    return [{"id": t.id, "title": t.title, "status": t.status, "priority": t.priority} for t in tasks]
