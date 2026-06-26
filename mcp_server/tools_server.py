"""
mcp_server/tools_server.py
Custom MCP Server exposing concierge tools to agents.
Demonstrates MCP integration — a key course concept.
"""

import json
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import storage
from security.protection import sanitize_input, validate_date_format, validate_priority, validate_application_status

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("[MCP] mcp package not installed. Running in mock mode.")

# ── MCP Server Definition ──────────────────────────────────

if MCP_AVAILABLE:
    app = Server("personal-career-concierge-mcp")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="add_study_task",
                description="Add a new study task with subject, deadline, and priority",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "subject": {"type": "string", "description": "Subject or topic name"},
                        "deadline": {"type": "string", "description": "Deadline in YYYY-MM-DD format"},
                        "priority": {"type": "string", "description": "Priority: HIGH, MEDIUM, or LOW"},
                        "notes": {"type": "string", "description": "Optional notes"}
                    },
                    "required": ["subject", "deadline", "priority"]
                }
            ),
            types.Tool(
                name="get_study_tasks",
                description="Get all study tasks, optionally filtered by status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "description": "Filter by: PENDING or DONE (optional)"}
                    }
                }
            ),
            types.Tool(
                name="add_application",
                description="Track a new job or internship application",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "company": {"type": "string"},
                        "role": {"type": "string"},
                        "applied_date": {"type": "string", "description": "YYYY-MM-DD format"},
                        "status": {"type": "string", "description": "Default: APPLIED"},
                        "notes": {"type": "string"}
                    },
                    "required": ["company", "role", "applied_date"]
                }
            ),
            types.Tool(
                name="get_applications",
                description="Get all job applications, optionally filtered by status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "description": "Optional filter status"}
                    }
                }
            ),
            types.Tool(
                name="add_reminder",
                description="Set a reminder for a study task or job application deadline",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "due_date": {"type": "string"},
                        "category": {"type": "string", "description": "STUDY or JOB"},
                        "message": {"type": "string"}
                    },
                    "required": ["title", "due_date", "category", "message"]
                }
            ),
            types.Tool(
                name="get_reminders",
                description="Get all reminders, optionally filtered by category",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "description": "STUDY or JOB (optional)"}
                    }
                }
            ),
        ]

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        result = _handle_tool(name, arguments)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    async def run_mcp_server():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())


# ── Tool Logic (shared with mock mode) ────────────────────

def _handle_tool(name: str, arguments: dict) -> dict:
    """Core tool logic — works in both MCP and mock mode."""
    try:
        if name == "add_study_task":
            subject = sanitize_input(arguments.get("subject", ""))
            deadline = arguments.get("deadline", "")
            priority = arguments.get("priority", "MEDIUM")
            notes = sanitize_input(arguments.get("notes", ""))
            
            if not validate_date_format(deadline):
                return {"error": "Invalid date format. Use YYYY-MM-DD"}
            if not validate_priority(priority):
                return {"error": "Priority must be HIGH, MEDIUM, or LOW"}
            
            task = storage.add_study_task(subject, deadline, priority, notes)
            return {"success": True, "task": task}

        elif name == "get_study_tasks":
            status = arguments.get("status")
            tasks = storage.get_study_tasks(status)
            return {"success": True, "tasks": tasks, "count": len(tasks)}

        elif name == "add_application":
            company = sanitize_input(arguments.get("company", ""))
            role = sanitize_input(arguments.get("role", ""))
            applied_date = arguments.get("applied_date", "")
            status = arguments.get("status", "APPLIED")
            notes = sanitize_input(arguments.get("notes", ""))
            
            if not validate_date_format(applied_date):
                return {"error": "Invalid date format. Use YYYY-MM-DD"}
            if not validate_application_status(status):
                return {"error": "Invalid status"}
            
            app_record = storage.add_application(company, role, applied_date, status, notes)
            return {"success": True, "application": app_record}

        elif name == "get_applications":
            status = arguments.get("status")
            apps = storage.get_applications(status)
            return {"success": True, "applications": apps, "count": len(apps)}

        elif name == "add_reminder":
            title = sanitize_input(arguments.get("title", ""))
            due_date = arguments.get("due_date", "")
            category = arguments.get("category", "STUDY")
            message = sanitize_input(arguments.get("message", ""))
            
            if not validate_date_format(due_date):
                return {"error": "Invalid date format. Use YYYY-MM-DD"}
            
            reminder = storage.add_reminder(title, due_date, category, message)
            return {"success": True, "reminder": reminder}

        elif name == "get_reminders":
            category = arguments.get("category")
            reminders = storage.get_reminders(category)
            return {"success": True, "reminders": reminders, "count": len(reminders)}

        else:
            return {"error": f"Unknown tool: {name}"}

    except Exception as e:
        return {"error": str(e)}


# ── Mock MCP Client (for agents when MCP not in stdio mode) ──

class MockMCPClient:
    """Simulates MCP tool calls for use inside Kaggle notebook."""
    
    def call(self, tool_name: str, **kwargs) -> dict:
        return _handle_tool(tool_name, kwargs)

# Singleton mock client
mcp_client = MockMCPClient()


if __name__ == "__main__":
    if MCP_AVAILABLE:
        import asyncio
        asyncio.run(run_mcp_server())
    else:
        print("MCP server requires 'mcp' package. Install with: pip install mcp")
