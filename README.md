# TaskMitra
**Personal Agentic AI assistant for Workflow Orchestration & Automation**

TaskMitra is a full-stack platform built to design and execute complex AI-driven workflows and automate the same. The core idea is to connect Large Language Models with real-world actions in a safe and controlled way. At the moment, the system is focused on Google Workspace (especially Gmail, sheets, drive) and Github. It includes a strong Human-in-the-Loop (HITL) approval layer for sensitive operations.

---

## Key Features (Current)

- **Multi Agents Logic**  
  Multiple AI agent capable of reasoning across multiple steps, invoking tools when required providing context.

- **Human-in-the-Loop (HITL)**  
  Explicit approval flows for high-risk actions such as sending emails on behalf of the user.

- **Google Integration**  
  Native OAuth support for Gmail, including reading, drafting, and sending emails.

- **Real-time Experience**  
  End-to-end streaming responses to provide a low-latency, chat-like user experience.

- **Secure Authentication**  
  JWT-based authentication with refresh token rotation for session safety.

- **Modern UI**  
  A clean, dark-themed, responsive interface built using Tailwind CSS and Shadcn UI.

---

## 🛠️ Tech Stack

### Backend (Server)
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with async SQLAlchemy
- **Agent System**: Custom Deep Agent implementation
- **Data Validation**: Pydantic v2
- **API Docs**: Scalar API Reference

### Frontend (Client)
- **Framework**: React + Vite + TypeScript
- **Styling**: Tailwind CSS & Shadcn UI
- **State Management**: TanStack Query (React Query)
- **Theming**: next-themes (dark mode by default)

---

## Future Roadmap

The project is currently in its **initial setup phase**. The next steps are focused on making the orchestration layer more powerful and scalable:

- [ ] **LangGraph Integration**  
  Transition from linear tool execution to cyclic, graph-based agent workflows.

- [ ] **Redis Integration**  
  For caching, coordination, and short-lived state management.

- [ ] **Celery Workers**  
  Background task execution for long-running and async workflows.

- [ ] **Multi-Agent Orchestration**  
  Dedicated agents for different domains such as Docs, Calendar, and other Google services.

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL

### Server Setup
1. Navigate to the `server/` directory  
2. Create a virtual environment: `python -m venv venv`  
3. Activate it:  
   - Linux/macOS: `source venv/bin/activate`  
   - Windows: `venv\Scripts\activate`  
4. Install dependencies: `pip install -r req.txt`  
5. Configure environment variables using the `.env` template inside `server/app/`  
6. Run the server: `fastapi dev app/main.py`

### Client Setup
1. Navigate to the `client/` directory  
2. Install dependencies: `npm install`  
3. Run the development server: `npm run dev`

---

## License
MIT License
