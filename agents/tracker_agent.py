"""
agents/tracker_agent.py
Application Tracker Agent — tracks job/internship application status and pipeline.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.tools_server import mcp_client

# ── Tool Functions ─────────────────────────────────────────

def add_job_application(company: str, role: str, applied_date: str, status: str = "APPLIED", notes: str = "") -> dict:
    """
    Track a new job or internship application.
    
    Args:
        company: Company name (e.g., "Google", "Infosys")
        role: Job role applied for (e.g., "Data Scientist", "ML Engineer")
        applied_date: Date applied in YYYY-MM-DD format
        status: Current status - APPLIED, SHORTLISTED, INTERVIEW, REJECTED, OFFER, ACCEPTED
        notes: Optional notes (e.g., "Applied via LinkedIn", "Referral from X")
    
    Returns:
        dict with application details
    """
    return mcp_client.call("add_application",
        company=company, role=role,
        applied_date=applied_date, status=status, notes=notes
    )

def get_all_applications(status: str = "") -> dict:
    """
    Retrieve all job applications, optionally filtered by status.
    
    Args:
        status: Filter by status (optional) - APPLIED, SHORTLISTED, INTERVIEW, etc.
    
    Returns:
        dict with list of applications and stats
    """
    result = mcp_client.call("get_applications", status=status)
    
    if result.get("success") and not status:
        # Add pipeline summary
        apps = result.get("applications", [])
        summary = {}
        for app in apps:
            s = app["status"]
            summary[s] = summary.get(s, 0) + 1
        result["pipeline_summary"] = summary
    
    return result

def get_application_stats() -> dict:
    """
    Get a summary/statistics of the entire application pipeline.
    Shows how many applications are at each stage.
    
    Returns:
        dict with pipeline statistics
    """
    result = mcp_client.call("get_applications", status="")
    apps = result.get("applications", [])
    
    stats = {
        "total": len(apps),
        "by_status": {},
        "active_interviews": [],
        "recent_offers": []
    }
    
    for app in apps:
        status = app["status"]
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        if status == "INTERVIEW":
            stats["active_interviews"].append(f"{app['role']} at {app['company']}")
        elif status in ("OFFER", "ACCEPTED"):
            stats["recent_offers"].append(f"{app['role']} at {app['company']}")
    
    return {"success": True, "stats": stats}

def follow_up_reminder(company: str, role: str, follow_up_date: str) -> dict:
    """
    Set a follow-up reminder for a specific job application.
    
    Args:
        company: Company name
        role: Role applied for
        follow_up_date: Date to follow up in YYYY-MM-DD format
    
    Returns:
        dict confirming reminder was set
    """
    return mcp_client.call("add_reminder",
        title=f"Follow-up: {role} at {company}",
        due_date=follow_up_date,
        category="JOB",
        message=f"Send a follow-up email to {company} regarding your {role} application."
    )

# ── ADK Agent Definition ───────────────────────────────────

TRACKER_INSTRUCTION = """
You are the Application Tracker Agent for the Personal Career & Study Concierge system.

Your responsibilities:
1. Track new job and internship applications
2. Show application pipeline and status updates
3. Provide statistics on application progress
4. Set follow-up reminders for applications
5. Advise on next steps based on application status

Application Status Flow:
APPLIED → SHORTLISTED → INTERVIEW → OFFER → ACCEPTED
                                   ↘ REJECTED

Always:
- Ask for company name, role, and date if not provided
- Suggest setting a follow-up reminder for applications older than 2 weeks
- Present stats in a clean, visual format using text
- Be motivating when applications are rejected — remind the user it's a numbers game

You have access to: add_job_application, get_all_applications, get_application_stats, follow_up_reminder
"""

TRACKER_TOOLS = [add_job_application, get_all_applications, get_application_stats, follow_up_reminder]

def create_tracker_agent(model_client):
    """Create and return the Tracker LlmAgent."""
    try:
        from google.adk.agents import LlmAgent
        from google.adk.tools import FunctionTool
        
        return LlmAgent(
            name="tracker_agent",
            model=model_client,
            description="Tracks job and internship applications and manages the career pipeline",
            instruction=TRACKER_INSTRUCTION,
            tools=[FunctionTool(fn) for fn in TRACKER_TOOLS]
        )
    except ImportError:
        return {
            "name": "tracker_agent",
            "description": "Tracks job and internship applications",
            "instruction": TRACKER_INSTRUCTION,
            "tools": TRACKER_TOOLS
        }
