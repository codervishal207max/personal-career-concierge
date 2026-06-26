"""
agents/reminder_agent.py
Reminder Agent — generates smart alerts for study deadlines and job application follow-ups.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.tools_server import mcp_client
from data import storage
from datetime import datetime, timedelta

# ── Tool Functions ─────────────────────────────────────────

def set_reminder(title: str, due_date: str, category: str, message: str) -> dict:
    """
    Set a new reminder for any upcoming task or deadline.
    
    Args:
        title: Short title for the reminder (e.g., "ML Exam Revision")
        due_date: Reminder date in YYYY-MM-DD format
        category: STUDY or JOB
        message: Detailed reminder message
    
    Returns:
        dict with reminder details
    """
    return mcp_client.call("add_reminder",
        title=title, due_date=due_date, category=category, message=message
    )

def get_all_reminders(category: str = "") -> dict:
    """
    Get all reminders, optionally filtered by category.
    
    Args:
        category: Optional filter - STUDY or JOB
    
    Returns:
        dict with list of reminders
    """
    return mcp_client.call("get_reminders", category=category)

def get_upcoming_deadlines(days_ahead: int = 7) -> dict:
    """
    Check all upcoming study and job deadlines within the next N days.
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
    
    Returns:
        dict with upcoming deadlines sorted by urgency
    """
    today = datetime.now().date()
    cutoff = today + timedelta(days=days_ahead)
    
    upcoming = []
    
    # Check study tasks
    tasks = storage.get_study_tasks("PENDING")
    for task in tasks:
        try:
            deadline = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
            if today <= deadline <= cutoff:
                days_left = (deadline - today).days
                upcoming.append({
                    "type": "STUDY",
                    "title": task["subject"],
                    "deadline": task["deadline"],
                    "days_left": days_left,
                    "priority": task["priority"],
                    "urgency": "🔴 URGENT" if days_left <= 2 else "🟡 SOON" if days_left <= 5 else "🟢 UPCOMING"
                })
        except:
            pass
    
    # Check job reminders
    reminders = storage.get_reminders("JOB")
    for rem in reminders:
        try:
            due = datetime.strptime(rem["due_date"], "%Y-%m-%d").date()
            if today <= due <= cutoff:
                days_left = (due - today).days
                upcoming.append({
                    "type": "JOB",
                    "title": rem["title"],
                    "deadline": rem["due_date"],
                    "days_left": days_left,
                    "message": rem["message"],
                    "urgency": "🔴 URGENT" if days_left <= 2 else "🟡 SOON" if days_left <= 5 else "🟢 UPCOMING"
                })
        except:
            pass
    
    # Sort by days_left
    upcoming.sort(key=lambda x: x["days_left"])
    
    return {
        "success": True,
        "period": f"Next {days_ahead} days",
        "total_upcoming": len(upcoming),
        "deadlines": upcoming
    }

def generate_daily_digest() -> dict:
    """
    Generate a daily summary of all pending tasks and upcoming deadlines.
    Shows today's priorities at a glance.
    
    Returns:
        dict with daily digest including tasks and reminders
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get all pending tasks
    tasks = storage.get_study_tasks("PENDING")
    apps = storage.get_applications()
    upcoming = get_upcoming_deadlines(7)
    
    active_interviews = [a for a in apps if a["status"] == "INTERVIEW"]
    pending_applications = [a for a in apps if a["status"] == "APPLIED"]
    
    digest = {
        "date": today,
        "study": {
            "total_pending": len(tasks),
            "high_priority": [t for t in tasks if t["priority"] == "HIGH"]
        },
        "career": {
            "total_applications": len(apps),
            "active_interviews": len(active_interviews),
            "pending_responses": len(pending_applications)
        },
        "urgent_deadlines": upcoming["deadlines"][:3],  # Top 3 most urgent
        "motivation": _get_motivation_message(len(tasks), len(active_interviews))
    }
    
    return {"success": True, "digest": digest}

def _get_motivation_message(task_count: int, interview_count: int) -> str:
    if interview_count > 0:
        return f"🎯 You have {interview_count} active interview(s)! Keep going — you're in the game!"
    if task_count > 5:
        return "📚 Lots to cover, but you've got this! Focus on HIGH priority tasks first."
    if task_count == 0:
        return "✅ No pending tasks! Great job staying on top of things."
    return "💪 Stay consistent — small daily progress leads to big results!"

# ── ADK Agent Definition ───────────────────────────────────

REMINDER_INSTRUCTION = """
You are the Reminder Agent for the Personal Career & Study Concierge system.

Your responsibilities:
1. Set reminders for study deadlines and job application follow-ups
2. Show upcoming deadlines (by default for next 7 days)
3. Generate a daily digest of all priorities
4. Alert users about urgent tasks (due within 2 days)

Always:
- Proactively check upcoming deadlines when user asks "what should I do today?"
- Use urgency indicators (🔴 URGENT, 🟡 SOON, 🟢 UPCOMING) in your responses
- Generate a daily digest if the user greets or asks for a summary
- Remind users to follow up on job applications after 2 weeks of no response

You have access to: set_reminder, get_all_reminders, get_upcoming_deadlines, generate_daily_digest
"""

REMINDER_TOOLS = [set_reminder, get_all_reminders, get_upcoming_deadlines, generate_daily_digest]

def create_reminder_agent(model_client):
    """Create and return the Reminder LlmAgent."""
    try:
        from google.adk.agents import LlmAgent
        from google.adk.tools import FunctionTool
        
        return LlmAgent(
            name="reminder_agent",
            model=model_client,
            description="Generates smart reminders and daily digests for study and career deadlines",
            instruction=REMINDER_INSTRUCTION,
            tools=[FunctionTool(fn) for fn in REMINDER_TOOLS]
        )
    except ImportError:
        return {
            "name": "reminder_agent",
            "description": "Generates smart reminders and daily digests",
            "instruction": REMINDER_INSTRUCTION,
            "tools": REMINDER_TOOLS
        }
