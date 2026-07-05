# OmniQuery AI

**A smart multi-agent system that understands user queries and dynamically selects the best data source — documents, database, or web — to generate accurate answers using local LLMs.**

Built by **[Krisha Arya](https://www.linkedin.com/in/krisha-arya/)**.

---

## Watch the demo

See OmniQuery in action in this LinkedIn walkthrough:

**[OmniQuery AI — Video demo & project introduction](https://www.linkedin.com/posts/krisha-arya_ai-llm-rag-ugcPost-7455327070177361920-p1df/)**

> *"A smart multi-agent system that understands user queries and dynamically selects the best source (Docs, DB, Web) to generate accurate responses using LLMs."*

---

## What is OmniQuery?

Most chatbots use **one** LLM prompt and hope it figures out where the answer lives. OmniQuery takes a different approach.

When you ask a question, a **central orchestrator** (built with LangGraph) figures out what kind of question it is, picks the right specialist agent, runs it, and returns a single answer with **citations** showing which source was used.

| You ask… | OmniQuery routes to… |
|----------|----------------------|
| *"What is the company leave policy?"* | **DocAgent** — searches PDFs/policies in ChromaDB |
| *"Show me all employees"* | **DBAgent** — runs SQL on PostgreSQL |
| *"What is the weather today?"* | **WebSearchAgent** — searches the web via DuckDuckGo |

The system is designed for **enterprise-style scenarios**: internal documents, structured employee data, role-based permissions, and optional web fallback — all running on **local Ollama models** so sensitive data never leaves your machine.

---

## Key features

- **Multi-agent orchestration** — LangGraph state machine: preprocess → classify → execute → synthesize → format
- **Rule-based intent routing** — fast, deterministic classification (no LLM call just to pick an agent)
- **Role-based access control (RBAC)** — `user`, `admin`, and `superadmin` roles control SELECT / UPDATE / INSERT / DELETE on the database
- **Document RAG** — ChromaDB vector search + Flashrank reranking over company PDFs
- **Database agent** — natural language to SQL with a custom ReAct tool loop tuned for small local models
- **Web fallback** — DuckDuckGo search when document and database agents cannot answer
- **JWT authentication** — login, register, and role-aware query API
- **Web UI** — simple HTML/JS frontend at `http://localhost:8000`

---

## Architecture (high level)

```
                    ┌─────────────┐
                    │   Browser   │
                    │  or API     │
                    └──────┬──────┘
                           │  POST /api/v1/query + JWT
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    └──────┬──────┘
                           ▼
              ┌────────────────────────┐
              │  LangGraph Orchestrator │
              │                        │
              │  classify → route      │
              │  → execute agent(s)    │
              │  → synthesize answer   │
              └───────────┬────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────┐    ┌──────────────┐
   │ DocAgent │    │ DBAgent  │    │ WebSearch    │
   │ ChromaDB │    │ Postgres │    │ DuckDuckGo   │
   │ Flashrank│    │ ReAct+SQL│    │              │
   └──────────┘    └──────────┘    └──────────────┘
```

### The three live agents

| Agent | Purpose | Tech |
|-------|---------|------|
| **DocAgent** | HR policies, handbooks, internal PDFs | ChromaDB, `nomic-embed-text`, Flashrank |
| **DBAgent** | Employee records, salaries, analytics | PostgreSQL, custom ReAct engine, SQL tools |
| **WebSearchAgent** | Real-time / public knowledge | DuckDuckGo, LLM summarization |

> **Note:** A **ConfluenceAgent** is implemented but **disabled by default** (requires Atlassian API credentials in `config.yaml`).

---

## How a query flows (simple explanation)

1. **You send a question** to `POST /api/v1/query` (optionally with a JWT bearer token).
2. **Classify** scores the query with weighted keywords and regex guardrails — e.g. *policy* → documents, *salary* → database, *weather* → web.
3. **RBAC check** — if you ask to DELETE but your role only allows SELECT, the request is denied immediately (no LLM, no SQL).
4. **Router** asks each agent *"how confident are you?"* and builds an execution plan.
5. **Execute** runs the best agent(s) in order.
6. **Synthesize** merges results into one Markdown answer with source citations.
7. **Fallback** — if every agent fails, WebSearch or a bare LLM attempt is used as last resort.

---

## Example queries to try

| Query | Expected behavior |
|-------|-------------------|
| `show me all employees` | DBAgent fast-path SQL |
| `what is the company leave policy?` | DocAgent RAG |
| `what is the average salary?` | DBAgent |
| `what is the weather today?` | WebSearchAgent |
| `delete employee x@company.com` as `admin` | Permission denied (RBAC) |
| `what is Pooja Iyer's email address?` | DBAgent SELECT (not INSERT) |

---

## Tech stack

| Layer | Technologies |
|-------|----------------|
| API | FastAPI, Uvicorn, PyJWT |
| Orchestration | LangGraph, LangChain |
| LLM | Ollama (`llama3.2:1b` by default) |
| Embeddings | `nomic-embed-text` via Ollama |
| Vector DB | ChromaDB |
| Reranking | Flashrank |
| Database | PostgreSQL |
| Web search | DuckDuckGo (`ddgs`) |
| Frontend | HTML, CSS, JavaScript |

---

## Project structure

```
OmniQuery-AI-main/
├── README.md                    ← You are here
├── ROUND3_INTERVIEW_KIT.md      ← Technical deep-dive / interview prep
└── company-rag/                 ← Main application
    ├── src/
    │   ├── main.py              ← FastAPI entry point
    │   ├── agents/              ← DocAgent, DBAgent, WebSearchAgent, react_engine.py
    │   ├── core/orchestrator/   ← LangGraph graph, classify, router, synthesize
    │   ├── api/                 ← Auth (login, register, JWT)
    │   ├── ingestion/           ← PDF loading, chunking, embedding
    │   └── llm/                 ← Ollama provider factory
    ├── web/                     ← Frontend UI
    ├── scripts/                 ← DB seed scripts
    ├── requirements.txt
    └── config.yaml              ← Agents, models, DB URL (create/configure locally)
```

---

## Getting started

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) running locally
- PostgreSQL with the demo database (see `company-rag/scripts/`)

### 1. Install dependencies

```bash
cd OmniQuery-AI-main/company-rag
pip install -r requirements.txt
```

### 2. Pull Ollama models

```bash
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

### 3. Configure the app

Create or edit `company-rag/config.yaml` with your database URL, agent settings, and model names.

### 4. Seed the database (first time)

```bash
python scripts/create_demo_db.py
python scripts/seed_postgres.py
```

### 5. Run the server

```bash
python src/main.py
```

Open **http://localhost:8000** in your browser, log in, and start asking questions.

### API quick test

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "yourpassword"}'

# Query (replace TOKEN)
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"query": "show me all employees"}'
```

---

## Engineering highlights

These are real problems solved in this codebase — useful if you're reviewing the architecture:

| Challenge | Approach |
|-----------|----------|
| Wrong routing (*"stock"* in *"stock options policy"*) | Weighted keyword scoring + real-time regex guardrails |
| Substring bugs (*"address"* containing *"add"*) | Word-boundary matching for SQL intent detection |
| Small LLM breaks LangChain ReAct | Custom forgiving `ReActEngine` in `src/agents/react_engine.py` |
| Expired JWT demoted superadmin to `user` | Re-decode signed payload with `verify_exp: False` on query endpoint |
| Unauthorized DB mutations | RBAC enforced at classify time before any agent runs |


