import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.db_agent.agent import DBAgent, AgentContext
from src.llm.provider_factory import LLMProviderFactory
from src.config.config_loader import load_config
import logging

logging.basicConfig(level=logging.INFO)

async def run_db_test():
    config = load_config("config.yaml")
    llm = LLMProviderFactory.create(config.get("llm", {}))
    
    agent = DBAgent(
        config={"db_url": "postgresql://omniquery:omniquery123@localhost:5432/omniquery_demo", "db_type": "postgresql"},
        llm_provider=llm
    )
    
    await agent.initialize()
    
    ctx = AgentContext(
        query="Update Sneha Reddy's salary to 90000",
        original_query="Update Sneha Reddy's salary to 90000",
        user_role="admin"  # Let's test with admin
    )
    
    print("\n--- EXECUTION ---")
    res = await agent.execute(ctx)
    print("Answer:\n", res.answer)

if __name__ == "__main__":
    asyncio.run(run_db_test())
