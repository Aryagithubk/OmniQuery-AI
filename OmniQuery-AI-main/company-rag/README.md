# OmniQuery-AI

A comprehensive, multi-agent Retrieval-Augmented Generation (RAG) system uniquely designed to seamlessly synthesize data from multiple enterprise sources—from internal documents to database records and external knowledge. 

---

## 🌟 Project Overview

**OmniQuery** employs a **Multi-Agent Orchestrator Model**. Instead of relying on a single Large Language Model prompt to "do everything," the user query is handed to a centralized **Manager (Orchestrator)** which routes it to domain-specific **Agents**. These agents specialize in distinct types of information retrieval:

1. **📄 DocAgent**: Dedicated to policy documents, wikis, and textual data via Vector DB search.
2. **🗃️ DBAgent**: Analyzes tabular and relational data in Postgres databases via LLM-to-SQL logic.
3. **🌐 WebSearchAgent**: Fetches real-time internet data as a fallback.
4. **📘 ConfluenceAgent** *(In Development)*: Intended for live internal organizational wikis.

---

## 🏗️ System Flow & Logic

The entire lifecycle of a user query moves through the **LangGraph Orchestrator**.

### Step-by-Step Flow:
1. **API Layer (Entry)**: A user submits a query `POST /api/v1/query`. Initial authentication and Role-Based Access Control (RBAC) extracts the user's role.
2. **Preprocess Node**: The query is normalized (correcting typos, standardizing symbols).
3. **Classify Node (Intent Detection)**: The LLM analyzes the query and determines the central *intent*—for example, "Is this a database question (e.g., getting a list of salaries) or a document question (e.g., HR policy)?"
4. **Router**: Analyzes the intent against all registered Agents. Each Agent calculates a `can_handle(query)` score (Confidence Score). The Orchestrator sorts the Agents and selects the primary capability.
5. **Execute Node**: 
   - Hands the query to the chosen Agent.
   - If the Agent successfully pulls data, execution proceeds.
   - If the Agent fails or hallucinates, the Orchestrator records the error and loops to the *next highest-scoring Agent*, simulating fallback resilience.
6. **Synthesize Node**: Consolidates raw data retrieved by the respective agent(s) into a unified, human-readable paragraph formatted in Markdown.
7. **Fallback Node**: If all agents completely fail to answer the query, a final LLM-pass is executed as a "best effort" answer.
8. **Final Response**: Returned to the frontend with citations detailing which Agent answered it and execution times.

---

## 🤖 Deeper Dive: The Agents & Their Logic

### 1. Document Agent (DocAgent)
- **Logic**: Implements localized RAG. Converts documents (PDFs, TXTs) into mathematical vectors during setup. When a query is asked, it searches the `ChromaDB` for the three most relevant textual chunks, reranks them using `Flashrank`, and synthesizes a sourced claim.
- **Libraries/Tools**: `langchain`, `chromadb`, `flashrank`, `pypdf`.

### 2. Database Agent (DBAgent)
- **Logic**: Connects directly to a PostgreSQL database. It looks at the schema, translates the English user query into an optimized SQL command, runs the query safely respecting user limits/roles, and translates the rows returned into an English summary.
- **Libraries/Tools**: `psycopg2-binary`, `langchain`, LLM prompt logic preventing malicious behavior (SQL injection guards).

### 3. Web Agent (WebSearchAgent)
- **Logic**: Engaged as a fallback or if the query strictly requests internet knowledge.
- **Libraries/Tools**: `duckduckgo-search`.

### 4. Confluence Agent (How It Will Work)
*Note: Currently a concept/skeleton, here is its architectural design.*
- **Logic**: Directly authenticates securely into Atlassian Confluence via a personal access token. When users query blog posts or dynamic team wikis, it:
   1. Uses the Confluence API/CQL (Confluence Query Language) to search for spaces and titles.
   2. Receives heavily structured HTML representations of the pages.
   3. Uses `beautifulsoup4` to strip out the HTML to plain semantic markdown.
   4. Splits that markdown via LangChain Text Splitters.
   5. Answers and cites the precise internal wiki page URL.
- **Libraries/Tools**: `requests`, `beautifulsoup4`, `langchain-text-splitters`.

---

## 🛠️ Technology Stack & Libraries Used

### Backend Framework
- **FastAPI / Uvicorn**: High-performance asynchronous API hosting the application.
- **Python-Multipart / PyJWT / Passlib**: Handling secure authentication and payload parsing.

### LLM Orchestration & State
- **LangGraph**: Defines the nodes, state clipboard, and cyclic flow manager.
- **LangChain / LangChain-Community**: Wrapping tool sets, defining prompts seamlessly, and simplifying interactions with the Vector DB.

### AI & Data
- **Ollama**: Allows keeping privacy by hosting the LLM locally on bare metal.
- **ChromaDB**: High-performance local Vector store.
- **Flashrank**: Extremely lightweight cross-encoder to improve search results.

---

## 🚀 Setup & Execution

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Pull Local Models (Ollama)**:
   Ensure Ollama is running, then pull the LLM and Embedding models defined in `config.yaml`:
   ```bash
   ollama pull llama3.2:1b
   ollama pull nomic-embed-text
   ```

3. **Start the Application**:
   ```bash
   python src/main.py
   ```
   *The server defaults to running on port 8000 via Uvicorn. Access the web UI via `http://localhost:8000`.*
