import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.db_agent.agent import DBAgent
from src.agents.web_agent.agent import WebSearchAgent
from src.agents.doc_agent.agent import DocAgent
from src.agents.base_agent import AgentContext
from src.llm.provider_factory import LLMProviderFactory
from src.config.config_loader import load_config

async def run_tests():
    config = load_config("config.yaml")
    llm = LLMProviderFactory.create(config.get("llm", {}))
    
    print("Initializing Agents...")
    db_agent = DBAgent(
        config={"db_url": "postgresql://omniquery:omniquery123@localhost:5432/omniquery_demo", "db_type": "postgresql"},
        llm_provider=llm
    )
    await db_agent.initialize()
    
    web_agent = WebSearchAgent(
        config={"max_results": 2},
        llm_provider=llm
    )
    await web_agent.initialize()
    
    doc_agent = DocAgent(
        config={
            "embedding_model": config.get("embedding", {}).get("model", "nomic-embed-text"),
            "persist_directory": config.get("vector_db", {}).get("persist_directory", "./vector_store"),
            "top_k": 3,
        },
        llm_provider=llm
    )
    await doc_agent.initialize()
    
    print("\n==================================")
    print("TEST 1: DB Agent - Hallucination Check (Non-existent employee)")
    print("==================================")
    ctx_db = AgentContext(
        query="What is the salary of the employee named John Zoidberg who does not exist?",
        original_query="What is the salary of the employee named John Zoidberg who does not exist?",
        user_role="admin",
        intent="data_query"
    )
    res_db = await db_agent.execute(ctx_db)
    print(f"DBAgent Answer:\n{res_db.answer}\n")
    
    print("\n==================================")
    print("TEST 2: Web Agent - Hallucination Check (Vague/Impossible query)")
    print("==================================")
    ctx_web = AgentContext(
        query="What is the exact square footage of the mars rover's hidden coffee machine from 2085?",
        original_query="What is the exact square footage of the mars rover's hidden coffee machine from 2085?",
        user_role="user",
        intent="web_search"
    )
    res_web = await web_agent.execute(ctx_web)
    print(f"WebAgent Answer:\n{res_web.answer}\n")
    
    print("\n==================================")
    print("TEST 3: Doc Agent - Hallucination Check (Fictitious Policy)")
    print("==================================")
    ctx_doc = AgentContext(
        query="What does the company policy say about bringing pet dragons to the office on Fridays?",
        original_query="What does the company policy say about bringing pet dragons to the office on Fridays?",
        user_role="user",
        intent="document_search"
    )
    res_doc = await doc_agent.execute(ctx_doc)
    print(f"DocAgent Answer:\n{res_doc.answer}\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
