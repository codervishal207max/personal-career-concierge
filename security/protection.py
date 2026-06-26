"""
security/protection.py
Input validation and data protection layer.
Demonstrates security features required by the capstone.
"""

import re
import hashlib
import hmac
import os
from typing import Any, Dict

# ── Input Sanitization ─────────────────────────────────────

DANGEROUS_PATTERNS = [
    r"<script.*?>.*?</script>",   # XSS
    r"(DROP|DELETE|INSERT|UPDATE|SELECT)\s+TABLE",  # SQL injection
    r"\.\./",                     # Path traversal
    r"__import__",                # Python code injection
    r"eval\s*\(",                 # eval injection
]

def sanitize_input(text: str) -> str:
    """Remove dangerous patterns from user input."""
    if not isinstance(text, str):
        return str(text)
    
    sanitized = text.strip()
    for pattern in DANGEROUS_PATTERNS:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    # Limit length
    return sanitized[:500]

def validate_date_format(date_str: str) -> bool:
    """Validate date is in YYYY-MM-DD format."""
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    return bool(re.match(pattern, date_str.strip()))

def validate_priority(priority: str) -> bool:
    """Validate priority is one of: HIGH, MEDIUM, LOW."""
    return priority.upper() in ["HIGH", "MEDIUM", "LOW"]

def validate_application_status(status: str) -> bool:
    """Validate job application status."""
    valid = ["APPLIED", "SHORTLISTED", "INTERVIEW", "REJECTED", "OFFER", "ACCEPTED"]
    return status.upper() in valid

# ── Data Protection ────────────────────────────────────────

_SECRET_KEY = os.environ.get("SECRET_KEY", "concierge-default-secret-key-2026")

def hash_sensitive_data(data: str) -> str:
    """One-way hash for sensitive info (emails, phone numbers)."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()[:16]

def generate_hmac_token(data: str) -> str:
    """Generate HMAC token for data integrity verification."""
    return hmac.new(
        _SECRET_KEY.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

def verify_hmac_token(data: str, token: str) -> bool:
    """Verify data integrity using HMAC."""
    expected = generate_hmac_token(data)
    return hmac.compare_digest(expected, token)

# ── Access Control ─────────────────────────────────────────

_ALLOWED_AGENTS = {"planner_agent", "tracker_agent", "reminder_agent", "coordinator"}

def verify_agent_access(agent_name: str) -> bool:
    """Ensure only registered agents can access data tools."""
    return agent_name.lower() in _ALLOWED_AGENTS

# ── Safe Wrapper ───────────────────────────────────────────

def secure_tool_call(agent_name: str, func, **kwargs) -> Dict[str, Any]:
    """
    Wrapper that:
    1. Verifies agent has access
    2. Sanitizes all string inputs
    3. Returns error dict if validation fails
    """
    if not verify_agent_access(agent_name):
        return {"error": f"Access denied for agent: {agent_name}"}
    
    # Sanitize all string arguments
    clean_kwargs = {}
    for k, v in kwargs.items():
        if isinstance(v, str):
            clean_kwargs[k] = sanitize_input(v)
        else:
            clean_kwargs[k] = v
    
    try:
        result = func(**clean_kwargs)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
