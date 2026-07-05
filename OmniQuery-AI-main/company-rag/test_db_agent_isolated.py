import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.db_agent.agent import DBAgent, AgentContext
from src.llm.provider_factory import LLMProviderFactory
from src.config.config_loader import load_config

async def run_db_test():
    config = load_config("config.yaml")
    llm = LLMProviderFactory.create(config.get("llm", {}))
    
    agent = DBAgent(
        config={"db_url": "postgresql://omniquery:omniquery123@localhost:5432/omniquery_demo", "db_type": "postgresql"},
        llm_provider=llm
    )
    
    await agent.initialize()
    
    ctx = AgentContext(
        query="remove role as superadmin from arjun sharma. email arjun.sharma@company.com. make role as user",
        original_query="remove role as superadmin from arjun sharma. email arjun.sharma@company.com. make role as user",
        user_role="superadmin"
    )
    
    print("\n--- SCORES ---")
    score = await agent.can_handle(ctx)
    print("can_handle score:", score)
    
    print("\n--- EXECUTION ---")
    res = await agent.execute(ctx)
    print("Success:", res.success)
    print("Error:", res.error)
    print("Raw Data:", res.raw_data)
    print("Answer:\n", res.answer)

if __name__ == "__main__":
    asyncio.run(run_db_test())
