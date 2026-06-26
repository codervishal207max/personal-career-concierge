"""
main.py
Personal Career & Study Concierge — Main Entry Point
Run this file to start the multi-agent concierge system.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("❌ ERROR: GOOGLE_API_KEY not found.")
    print("   Copy .env.example to .env and add your API key.")
    sys.exit(1)

print("🚀 Personal Career & Study Concierge")
print("=" * 50)

# ── Try ADK path ───────────────────────────────────────────
ADK_AVAILABLE = False
try:
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools import FunctionTool
    import google.generativeai as genai

    genai.configure(api_key=GOOGLE_API_KEY)
    MODEL = "gemini-2.0-flash"
    ADK_AVAILABLE = True
    print("✅ Google ADK loaded successfully")
except ImportError:
    print("⚠️  Google ADK not found — running in Gemini Direct mode")
    print("   Install ADK with: pip install google-adk")

# ── Import agents ──────────────────────────────────────────
from agents.planner_agent import create_planner_agent, PLANNER_TOOLS
from agents.tracker_agent import create_tracker_agent, TRACKER_TOOLS
from agents.reminder_agent import create_reminder_agent, REMINDER_TOOLS, generate_daily_digest
from agents.coordinator import create_coordinator, COORDINATOR_INSTRUCTION

# ── ADK Multi-Agent Mode ───────────────────────────────────

def run_adk_mode():
    """Full multi-agent mode using Google ADK."""
    model = MODEL
    
    planner = create_planner_agent(model)
    tracker = create_tracker_agent(model)
    reminder = create_reminder_agent(model)
    coordinator = create_coordinator(model, planner, tracker, reminder)
    
    session_service = InMemorySessionService()
    runner = Runner(
        agent=coordinator,
        app_name="personal_career_concierge",
        session_service=session_service
    )
    
    session_id = "user_session_001"
    user_id = "student_user"
    
    print("\n💼 Concierge ready! Type your request or 'quit' to exit.")
    print("   Examples: 'Add ML assignment', 'I applied to Google', 'What's due this week?'")
    print("-" * 50)
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ("quit", "exit", "bye"):
            print("Concierge: Goodbye! Stay focused and keep applying! 👋")
            break
        if not user_input:
            continue
        
        from google.genai import types as genai_types
        content = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=user_input)]
        )
        
        response_text = ""
        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        response_text += part.text
        
        print(f"\nConcierge: {response_text}")

# ── Gemini Direct Mode (Fallback) ─────────────────────────

def run_gemini_direct_mode():
    """
    Fallback mode using Gemini directly with function calling.
    Works without google-adk installed.
    """
    import google.generativeai as genai
    
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Collect all tools from all agents
    all_tools = PLANNER_TOOLS + TRACKER_TOOLS + REMINDER_TOOLS
    
    system_prompt = COORDINATOR_INSTRUCTION + "\n\nYou have direct access to all agent tools."
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        tools=all_tools,
        system_instruction=system_prompt
    )
    
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    print("\n💼 Concierge ready! Type your request or 'quit' to exit.")
    print("   Examples: 'Add ML assignment due 2026-07-15', 'I applied to Google for Data Scientist role on 2026-06-20'")
    print("-" * 50)
    
    # Welcome message
    try:
        welcome = chat.send_message("Generate a welcome message and today's digest.")
        print(f"\nConcierge: {welcome.text}")
    except Exception as e:
        print(f"\nConcierge: Welcome to your Personal Career & Study Concierge! How can I help you today?")
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ("quit", "exit", "bye"):
            print("Concierge: Goodbye! Stay focused and keep applying! 👋")
            break
        if not user_input:
            continue
        
        try:
            response = chat.send_message(user_input)
            print(f"\nConcierge: {response.text}")
        except Exception as e:
            print(f"\nConcierge: Sorry, I encountered an error: {e}")

# ── Entry Point ────────────────────────────────────────────

if __name__ == "__main__":
    if ADK_AVAILABLE:
        run_adk_mode()
    else:
        run_gemini_direct_mode()
