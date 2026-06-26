"""
data/storage.py
In-memory storage for study tasks and job applications.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional

# In-memory storage (resets on restart — safe for demo)
_study_tasks: List[Dict] = []
_applications: List[Dict] = []
_reminders: List[Dict] = []

# ── Study Tasks ────────────────────────────────────────────

def add_study_task(subject: str, deadline: str, priority: str, notes: str = "") -> Dict:
    task = {
        "id": len(_study_tasks) + 1,
        "subject": subject,
        "deadline": deadline,
        "priority": priority.upper(),
        "notes": notes,
        "created_at": datetime.now().isoformat(),
        "status": "PENDING"
    }
    _study_tasks.append(task)
    return task

def get_study_tasks(status: Optional[str] = None) -> List[Dict]:
    if status:
        return [t for t in _study_tasks if t["status"] == status.upper()]
    return _study_tasks.copy()

def update_task_status(task_id: int, status: str) -> Optional[Dict]:
    for task in _study_tasks:
        if task["id"] == task_id:
            task["status"] = status.upper()
            return task
    return None

# ── Job Applications ───────────────────────────────────────

def add_application(company: str, role: str, applied_date: str, status: str = "APPLIED", notes: str = "") -> Dict:
    app = {
        "id": len(_applications) + 1,
        "company": company,
        "role": role,
        "applied_date": applied_date,
        "status": status.upper(),
        "notes": notes,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    _applications.append(app)
    return app

def get_applications(status: Optional[str] = None) -> List[Dict]:
    if status:
        return [a for a in _applications if a["status"] == status.upper()]
    return _applications.copy()

def update_application_status(app_id: int, status: str, notes: str = "") -> Optional[Dict]:
    for app in _applications:
        if app["id"] == app_id:
            app["status"] = status.upper()
            app["last_updated"] = datetime.now().isoformat()
            if notes:
                app["notes"] = notes
            return app
    return None

# ── Reminders ─────────────────────────────────────────────

def add_reminder(title: str, due_date: str, category: str, message: str) -> Dict:
    reminder = {
        "id": len(_reminders) + 1,
        "title": title,
        "due_date": due_date,
        "category": category.upper(),
        "message": message,
        "created_at": datetime.now().isoformat(),
        "notified": False
    }
    _reminders.append(reminder)
    return reminder

def get_reminders(category: Optional[str] = None) -> List[Dict]:
    if category:
        return [r for r in _reminders if r["category"] == category.upper()]
    return _reminders.copy()
