"""
agents/planner_agent.py
Planner Agent — manages study tasks, course schedules, and academic deadlines.
Built using Google ADK LlmAgent pattern.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.tools_server import mcp_client
from security.protection import sanitize_input, validate_date_format, validate_priority

# ── Tool Functions (exposed to ADK) ───────────────────────

def add_study_task(subject: str, deadline: str, priority: str, notes: str = "") -> dict:
    """
    Add a new study task to the planner.
    
    Args:
        subject: Subject or topic name (e.g., "Machine Learning", "DBMS")
        deadline: Deadline in YYYY-MM-DD format
        priority: Priority level - HIGH, MEDIUM, or LOW
        notes: Optional notes about the task
    
    Returns:
        dict with task details or error message
    """
    return mcp_client.call("add_study_task",
        subject=subject, deadline=deadline, priority=priority, notes=notes
    )

def get_study_tasks(status: str = "") -> dict:
    """
    Retrieve all study tasks, optionally filtered by status.
    
    Args:
        status: Filter tasks by status - PENDING or DONE (leave empty for all)
    
    Returns:
        dict with list of tasks and count
    """
    return mcp_client.call("get_study_tasks", status=status)

def generate_study_plan(course_name: str, topics: str, exam_date: str) -> dict:
    """
    Generate a structured study plan by breaking course into weekly tasks.
    
    Args:
        course_name: Name of the course (e.g., "Data Structures")
        topics: Comma-separated list of topics to cover
        exam_date: Exam date in YYYY-MM-DD format
    
    Returns:
        dict with generated plan details
    """
    topic_list = [t.strip() for t in topics.split(",")]
    created = []
    
    for i, topic in enumerate(topic_list):
        # Distribute topics across weeks
        from datetime import datetime, timedelta
        exam_dt = datetime.strptime(exam_date, "%Y-%m-%d")
        days_before = (len(topic_list) - i) * 3
        task_deadline = (exam_dt - timedelta(days=days_before)).strftime("%Y-%m-%d")
        
        priority = "HIGH" if i >= len(topic_list) - 3 else "MEDIUM"
        
        result = mcp_client.call("add_study_task",
            subject=f"{course_name}: {topic}",
            deadline=task_deadline,
            priority=priority,
            notes=f"Week {i+1} topic"
        )
        if result.get("success"):
            created.append(result["task"])
    
    return {
        "success": True,
        "plan": f"Study plan created for '{course_name}'",
        "tasks_created": len(created),
        "tasks": created
    }

# ── ADK Agent Definition ───────────────────────────────────

PLANNER_INSTRUCTION = """
You are the Study Planner Agent for the Personal Career & Study Concierge system.

Your responsibilities:
1. Help users manage their academic subjects and study tasks
2. Add study tasks with deadlines and priorities
3. Generate structured study plans for courses
4. Show pending or completed tasks on request
5. Suggest study priorities based on upcoming deadlines

Always:
- Ask for the deadline in YYYY-MM-DD format if not provided
- Set priority based on urgency (exam within 1 week = HIGH, 2 weeks = MEDIUM, else LOW)
- Be encouraging and organized in your responses
- Format task lists clearly with deadline and priority info

You have access to these tools: add_study_task, get_study_tasks, generate_study_plan
"""

PLANNER_TOOLS = [add_study_task, get_study_tasks, generate_study_plan]

def create_planner_agent(model_client):
    """
    Create and return the Planner LlmAgent.
    Works with Google ADK's LlmAgent.
    """
    try:
        from google.adk.agents import LlmAgent
        from google.adk.tools import FunctionTool
        
        return LlmAgent(
            name="planner_agent",
            model=model_client,
            description="Manages study schedules, course deadlines, and academic task planning",
            instruction=PLANNER_INSTRUCTION,
            tools=[FunctionTool(fn) for fn in PLANNER_TOOLS]
        )
    except ImportError:
        # Fallback: return a simple dict-based agent config
        return {
            "name": "planner_agent",
            "description": "Manages study schedules, course deadlines, and academic task planning",
            "instruction": PLANNER_INSTRUCTION,
            "tools": PLANNER_TOOLS
        }
