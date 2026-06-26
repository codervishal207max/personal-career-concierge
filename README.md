# 🎓💼 Personal Career & Study Concierge

> **Kaggle AI Agents: Intensive Vibe Coding Capstone Project**  
> Track: **Concierge Agents**  
> Author: Vishal Fulbandhe | [GitHub](https://github.com/codervishal207max) | [LinkedIn](https://linkedin.com/in/vishal-fulbandhe-16662832b)

---

## 🎯 Problem Statement

Students and job seekers struggle to manage two parallel worlds simultaneously:
- **Academic life** — assignments, exams, deadlines, study plans
- **Career life** — job applications, interview tracking, follow-ups

Existing tools handle these separately. This concierge brings them together in one intelligent, conversational AI system.

---

## 🤖 Solution: Multi-Agent Architecture

A coordinator orchestrates 3 specialized agents, each with their own tools:

```
                    ┌─────────────────────┐
         User ────▶ │  COORDINATOR AGENT  │
                    │  (Root Orchestrator) │
                    └──────────┬──────────┘
                               │ delegates to
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   PLANNER    │  │   TRACKER    │  │   REMINDER   │
    │    AGENT     │  │    AGENT     │  │    AGENT     │
    │              │  │              │  │              │
    │ • Add tasks  │  │ • Add apps   │  │ • Set alerts │
    │ • Study plan │  │ • Get stats  │  │ • Daily digest│
    │ • Get tasks  │  │ • Pipeline   │  │ • Upcoming   │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                  │
           └─────────────────┴──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   MCP TOOL      │
                    │   SERVER        │
                    │ (Secure Access) │
                    └─────────────────┘
```

---

## 🔑 3 Course Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| **Multi-Agent System (ADK)** | Coordinator + 3 specialized sub-agents with distinct roles |
| **MCP Server** | Custom `MCPToolServer` exposing 9 tools to agents via structured calls |
| **Security Features** | Input sanitization, date/priority validation, HMAC verification, agent access control |

---

## 🚀 Quick Start

### Option A: Kaggle Notebook
1. Fork the notebook from Kaggle
2. Add `GOOGLE_API_KEY` in Kaggle Secrets
3. Run all cells

### Option B: Local Setup
```bash
git clone https://github.com/codervishal207max/personal-career-concierge
cd personal-career-concierge
pip install -r requirements.txt
cp .env.example .env
# Add your GOOGLE_API_KEY in .env
python main.py
```

---

## 💬 Example Interactions

```
User: Give me today's daily digest
Concierge: 📊 Here's your daily summary for 2026-06-26:
  📚 Study: 2 pending tasks (1 HIGH priority)
  💼 Career: 5 applications (2 active interviews!)
  🔴 Urgent: ML Assignment due in 2 days

User: Add Machine Learning assignment due 2026-07-05 HIGH priority
Concierge: ✅ Added! ML Assignment deadline set for July 5 (9 days away)

User: I applied to Google for Data Scientist role on 2026-06-20
Concierge: 💼 Tracked! Google - Data Scientist (APPLIED on June 20)
  💡 Tip: Set a follow-up reminder for July 4 (2 weeks after applying)
```

---

## 📁 Project Structure

```
personal-career-concierge/
├── main.py                    # Entry point (local run)
├── kaggle_notebook.py         # Kaggle submission notebook
├── requirements.txt
├── agents/
│   ├── coordinator.py         # Root orchestrator
│   ├── planner_agent.py       # Study planning agent
│   ├── tracker_agent.py       # Job application tracker
│   └── reminder_agent.py      # Reminders & digest agent
├── mcp_server/
│   └── tools_server.py        # MCP tool server
├── security/
│   └── protection.py          # Security layer
└── data/
    └── storage.py             # In-memory data storage
```

---

## 🛡️ Security Features

- **Input Sanitization** — Strips XSS, SQL injection, and path traversal patterns
- **Date Validation** — Enforces YYYY-MM-DD format for all deadlines
- **Agent Access Control** — Only registered agents can call MCP tools
- **HMAC Verification** — Data integrity verification for sensitive operations
- **Data Hashing** — Sensitive identifiers are one-way hashed

---

## 🛠️ Tech Stack

- **Google Gemini 2.0 Flash** — LLM backbone
- **Google ADK** — Multi-agent orchestration
- **MCP (Model Context Protocol)** — Tool server architecture
- **Python** — Core implementation

---

*Built for the Kaggle + Google 5-Day AI Agents: Intensive Vibe Coding Capstone Project, June 2026*
