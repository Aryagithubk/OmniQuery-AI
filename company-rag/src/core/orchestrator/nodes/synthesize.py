"""
Synthesize node — merges results from all agents into a single answer.
"""

from src.core.orchestrator.state import OmniQueryState
from src.utils.logger import setup_logger

logger = setup_logger("SynthesizeNode")


def make_synthesize_node(llm_provider):
    """Factory that creates synthesize node with access to LLM"""

    async def synthesize_node(state: OmniQueryState) -> dict:
        """Synthesize results from all agents into a coherent answer"""
        results = state.get("agent_results", [])
        agents_used = state.get("agents_used", [])

        if not results:
            return {
                "synthesized_answer": "I couldn't find a good answer from any of my data sources. "
                                      "Please try rephrasing your question.",
                "overall_confidence": 0.0,
                "final_sources": [],
            }

        # If only one agent succeeded, use its answer directly
        if len(results) == 1:
            r = results[0]
            return {
                "synthesized_answer": r.get("answer", "No answer available."),
                "overall_confidence": r.get("confidence", 0.0),
                "final_sources": r.get("sources", []),
            }

        # Multiple agents — merge results using LLM
        try:
            parts = []
            all_sources = []
            max_confidence = 0.0

            for r in results:
                answer = r.get("answer", "")
                if answer:
                    agent_name = r.get("metadata", {}).get("agent", "Unknown")
                    parts.append(f"[From agent]: {answer}")
                    all_sources.extend(r.get("sources", []))
                    max_confidence = max(max_confidence, r.get("confidence", 0.0))

            combined = "\n\n---\n\n".join(parts)
            prompt = (
                f"You have received answers from multiple data sources to the following query.\n\n"
                f"ANSWERS:\n{combined}\n\n"
                f"First, discard any answers that state they cannot answer the question or lack information. "
                f"Then, synthesize the remaining answers into a single, coherent, comprehensive response.\n"
                f"If all answers state they lack information, say 'I could not find an answer across the databases.'\n"
                f"If the valid answers complement each other, combine them. If they conflict, present both perspectives."
            )

            response = await llm_provider.generate(prompt)

            return {
                "synthesized_answer": response.text,
                "overall_confidence": round(max_confidence, 3),
                "final_sources": all_sources,
            }

        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            # Fallback: just concatenate answers
            fallback = "\n\n".join(r.get("answer", "") for r in results if r.get("answer"))
            return {
                "synthesized_answer": fallback or "Error synthesizing answer.",
                "overall_confidence": 0.0,
                "final_sources": [],
            }

    return synthesize_node
