# AI-Powered Planner
A calendar, agenda and project planner assisted by a conversational AI agent. The assistant manages projects, tasks and events on the user's behalf through natural language, backed by a two-agent architecture orchestrated as a stateful graph.

<img width="2142" height="969" alt="ai-powered-planner-ui" src="https://github.com/user-attachments/assets/3a2acd67-1949-4988-8419-c4123ed9d4d6" />

## Features
- **ReAct tool agent**: A ReAct-style agent reasons over the conversation, decides which actions to perform and executes them through tool calls, while a separate answer agent turns its internal report into the reply shown to the user.
- **Full CRUD over projects and tasks**: The agent can create, read, update and delete projects, tasks and events, including combined workflows such as creating a project together with its tasks in a single request.
- **Conversation memory**: Each conversation thread is checkpointed with LangGraph's SQLite saver, so the agent keeps context across turns.
- **Cautious tool use**: The tool agent never invents IDs, dates or missing arguments. Ambiguous references are resolved by listing candidates, destructive actions require explicit confirmation, and missing information is requested back from the user instead of assumed.
- **Clean separation between logic and wording**: The tool agent never writes to the user; the answer agent never calls tools or sees internal identifiers. This keeps user-facing replies consistent regardless of which tools were used underneath.
- **Full-stack**: An Angular frontend consumes the FastAPI backend over a REST endpoint, with a calendar, an agenda, a project/task board and an embedded chat assistant.

## Agents
| Agent | Responsibility |
|---|---|
| Tool Agent | Decides whether one or more tools are needed, executes them against the database, and writes a short internal status report |
| Answer Agent | Reads the internal report and writes the final, natural-language reply to the user |

## Conversational Flow
1. **User message**: The user's message is appended to the conversation thread, persisted via a SQLite checkpointer.
2. **Tool agent**: Interprets the request against the conversation history, resolves relative dates and named references, and calls the appropriate tools (project, task or workflow tools) to fulfill it.
3. **Status report**: The tool agent closes its turn with a strict `STATUS` / `DETAILS` report (`DONE`, `NEEDS_INFO`, `NEEDS_CONFIRMATION`, `AMBIGUOUS_MATCH` or `OUT_OF_SCOPE`), stripped of any ID or implementation detail.
4. **Answer agent**: Converts that report into a plain-text reply in the user's language, asking for missing information, confirming destructive actions, or presenting ambiguous matches as needed.

## Tools
| Category | Tools |
|---|---|
| Projects | `create_project`, `update_project`, `get_project`, `list_projects`, `delete_project` |
| Tasks | `create_task`, `update_task`, `get_task`, `list_tasks`, `list_tasks_by_day`, `delete_task` |
| Workflows | `create_project_with_tasks` |

## Frontend
The interface is an Angular application that communicates with the backend through a REST endpoint.
- **Calendar and agenda views**: Tasks and events are displayed on a monthly calendar and on a day-by-day agenda.
- **Project and task management**: Dedicated views and modals to create, edit and organize projects and tasks.
- **Embedded chat assistant**: A chatbot panel lets the user manage their planner conversationally.

## Tech Stack
- **Backend**: FastAPI, LangGraph, LangChain
- **Frontend**: Angular
- **LLM**: Ollama (local)
- **Database**: SQLite (via SQLModel/SQLAlchemy), with Alembic migrations

## Project Structure
```
src/
├── backend/
│   ├── chatbot/
│   │   ├── chains.py                # LLM and agent definitions
│   │   ├── nodes.py                 # Node implementations for the graph
│   │   └── prompts_builder.py       # Prompt assembly for both agents
│   ├── config/
│   │   └── config.py                # Centralized configuration
│   ├── db/
│   │   ├── database.py              # Database session management
│   │   └── migrations/              # Alembic migrations
│   ├── models/
│   │   ├── project.py               # Project ORM model and schemas
│   │   └── task.py                  # Task ORM model and schemas
│   ├── prompts/
│   │   └── prompts.py               # Tool agent and answer agent prompt templates
│   ├── routes/
│   │   ├── chat.py                  # Chat endpoint
│   │   ├── health.py                # Health check endpoint
│   │   ├── projects.py              # Project REST endpoints
│   │   └── tasks.py                 # Task REST endpoints
│   ├── schemas/
│   │   ├── context.py               # Shared runtime context definition
│   │   ├── enums.py                 # Task type and color enums
│   │   ├── message.py               # Request/response payloads
│   │   └── state.py                 # Shared graph state definition
│   ├── services/
│   │   ├── graph_service.py         # Graph construction and routing
│   │   ├── project_service.py       # Project business logic
│   │   └── task_service.py          # Task business logic
│   ├── tools/
│   │   ├── project_tools.py         # Project management tools
│   │   ├── task_tools.py            # Task management tools
│   │   └── workflow_tools.py        # Combined multi-entity tools
│   └── main.py                      # FastAPI entry point
└── frontend/
    └── src/
        ├── app/                     # Application shell and routing
        ├── components/
        │   ├── agenda/              # Day-by-day agenda view
        │   ├── calendar/            # Monthly calendar view
        │   ├── chatbot/             # Embedded chat assistant
        │   ├── dashboard/           # Overview dashboard
        │   ├── projects/            # Project list and modals
        │   └── tasks/               # Task list and modals
        ├── models/                  # TypeScript data models
        └── services/                # API client services
```

## Configuration
Key parameters, defined in `src/backend/config/config.py`:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Connection string for the application's SQLite database |
| `CHECKPOINT_DB_PATH` | Path to the SQLite database used for conversation checkpointing |
| `LLM_MODEL` | Ollama model used by both the tool agent and the answer agent |
| `CHAT_TIMEOUT_SECONDS` | Maximum time allowed for a single conversational turn |
| `CORS_ORIGINS` | Allowed origins for the frontend to call the backend |

## Setup

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com) installed locally, with the target model pulled (e.g. `ollama pull qwen3:14b`)

### 2. Backend
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `src/backend/` with:

```
CORS_ORIGINS=http://localhost:4200
```

### 3. Apply database migrations
```bash
alembic upgrade head
```

### 4. Run the backend
```bash
uvicorn src.backend.main:app --reload
```

### 5. Run the frontend
```bash
cd src/frontend
npm install
npm start
```

## Licensing
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

It relies on external models with their own licensing terms:

- **LLM model**: Inference is performed locally through Ollama using Alibaba's Qwen3, distributed under the [Apache License 2.0](https://ollama.com/library/qwen3:latest/blobs/d18a5cc71b84).
