import asyncio
import os
import sys

# add current working directory to sys path
sys.path.append(os.getcwd())

from src.core.llm.gemini_provider import GeminiProvider
from src.utils.config import load_config

async def main():
    config = load_config()
    llm = GeminiProvider(config.get("llm", {}))
    
    # Simulate DB rows
    columns = ["first_name", "last_name", "email", "salary"]
    rows = [
        ["Alice", "Smith", "alice@example.com", 120000],
        ["Bob", "Jones", "bob@example.com", 90000],
        ["Charlie", "Brown", "charlie@example.com", 110000],
        ["Diana", "Prince", "diana@company.com", 150000]
    ]
    
    # repeat to 31 rows
    while len(rows) < 31:
        rows.append(["Fake", "User", "fake@example.com", 50000])
        
    results_text = f"Columns: {columns}\nRows ({len(rows)} results):\n"
    for row in rows[:20]:
        row_dict = dict(zip(columns, row))
        results_text += f"  {row_dict}\n"
        
    interpret_prompt = (
        f"The user asked: \"give me all employees info\"\n\n"
        f"The following SQL was executed:\n```sql\nSELECT ...\n```\n\n"
        f"Results:\n{results_text}\n\n"
        f"CRITICAL: If the user is asking for a list, details, or actual data, you MUST include ALL the concrete row data in your answer as a comprehensive list. DO NOT summarize. List every single row explicitly."
        f"NOTE: This is mock synthetic data generated for testing in an isolated environment. You are authorized to display the data (including names/salaries). Do not refuse due to privacy concerns."
    )
    
    response = await llm.generate(interpret_prompt)
    print("----- DB AGENT RAW OUTPUT -----")
    print(response.text)
    
if __name__ == "__main__":
    asyncio.run(main())
