import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.config_loader import load_config
from src.llm.provider_factory import LLMProviderFactory
from src.agents.agent_registry import AgentRegistry
from src.agents.doc_agent.agent import DocAgent
from src.agents.web_agent.agent import WebSearchAgent
from src.core.orchestrator.router import AgentRouter
from src.core.orchestrator.graph import build_orchestrator_graph

async def main():
    config = load_config("config.yaml")
    llm = LLMProviderFactory.create(config.get("llm", {}))
    
    registry = AgentRegistry()
    
    doc_config = config.get("agents", {}).get("doc_agent", {})
    doc_agent = DocAgent(
        config={
            "embedding_model": config.get("embedding", {}).get("model", "nomic-embed-text"),
            "persist_directory": config.get("vector_db", {}).get("persist_directory", "./vector_store"),
            "top_k": config.get("app", {}).get("top_k", 3),
        },
        llm_provider=llm,
    )
    registry.register(doc_agent)
    
    web_config = config.get("agents", {}).get("web_agent", {})
    web_agent = WebSearchAgent(
        config={"max_results": web_config.get("max_results", 5)},
        llm_provider=llm,
    )
    registry.register(web_agent)
    
    await registry.initialize_all()
    
    orchestrator_config = config.get("orchestrator", {})
    router = AgentRouter(
        agents=registry.get_all(),
        min_confidence=orchestrator_config.get("min_agent_confidence", 0.3),
        max_parallel=orchestrator_config.get("max_parallel_agents", 2),
    )
    
    graph = build_orchestrator_graph(router, registry, llm)
    
    initial_state = {
        "query": "tell me about elon musk",
        "original_query": "tell me about elon musk",
        "session_id": "",
        "intent": "",
        "entities": {},
        "agent_plans": [],
        "current_agent_index": 0,
        "agent_results": [],
        "failed_agents": [],
        "synthesized_answer": "",
        "final_sources": [],
        "agents_used": [],
        "overall_confidence": 0.0,
        "formatted_response": "",
        "execution_time_ms": 0.0,
        "error": None,
    }
    
    result = await graph.ainvoke(initial_state)
    
    print("\n--- AGENT PLANS ---")
    for p in result.get("agent_plans", []):
        print(f"{p['agent_name']}: {p['confidence']}")
        
    print("\n--- AGENT RESULTS ---")
    for r in result.get("agent_results", []):
        print(f"Answer: {r['answer'][:100]}...")
        print(f"Conf: {r['confidence']}")
        
    print("\n--- SYNTHESIZED FINAL ---")
    print(result.get("formatted_response", result.get("synthesized_answer")))
    
if __name__ == "__main__":
    asyncio.run(main())
