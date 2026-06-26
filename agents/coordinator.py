"""
agents/coordinator.py
Coordinator Agent — root orchestrator that routes user requests to the correct sub-agent.
This is the main entry point for the multi-agent system.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

COORDINATOR_INSTRUCTION = """
You are the Personal Career & Study Concierge — a smart assistant that helps students 
and job seekers manage their academic life and career journey from one place.

You coordinate between three specialized agents:

1. **planner_agent** — Study planning, subject deadlines, course schedules
   → Use for: "Add Machine Learning assignment", "Show my pending tasks", "Create study plan for DSA"

2. **tracker_agent** — Job/internship application tracking
   → Use for: "I applied to Google", "Show my applications", "Update interview status", "Application stats"

3. **reminder_agent** — Smart reminders and daily digest
   → Use for: "What's due this week?", "Give me today's digest", "Set a reminder", "Urgent tasks?"

Your job:
- Understand user intent and delegate to the RIGHT agent
- Combine responses from multiple agents when needed (e.g., daily digest = study + career together)
- Keep responses concise and actionable
- Start every session by offering a Daily Digest

Routing rules:
- Keywords like "study", "exam", "assignment", "course", "subject" → planner_agent
- Keywords like "applied", "interview", "company", "job", "internship", "offer" → tracker_agent  
- Keywords like "reminder", "deadline", "upcoming", "digest", "today", "urgent" → reminder_agent
- "How am I doing?" or "Summary" → call reminder_agent for digest

Always be friendly, structured, and motivating. You are a personal concierge — make the user feel supported!
"""

def create_coordinator(model_client, planner, tracker, reminder):
    """
    Create the root coordinator agent with sub-agents attached.
    
    Args:
        model_client: Gemini model client
        planner: Planner sub-agent
        tracker: Tracker sub-agent  
        reminder: Reminder sub-agent
    
    Returns:
        Coordinator LlmAgent (root agent)
    """
    try:
        from google.adk.agents import LlmAgent
        
        return LlmAgent(
            name="coordinator",
            model=model_client,
            description="Personal Career & Study Concierge — orchestrates study planning, job tracking, and smart reminders",
            instruction=COORDINATOR_INSTRUCTION,
            sub_agents=[planner, tracker, reminder]
        )
    except ImportError:
        # Fallback for environments without ADK
        return {
            "name": "coordinator",
            "description": "Personal Career & Study Concierge",
            "instruction": COORDINATOR_INSTRUCTION,
            "sub_agents": [planner, tracker, reminder]
        }
