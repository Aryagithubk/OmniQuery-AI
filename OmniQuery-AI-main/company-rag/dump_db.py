import psycopg2
import os

def dump_table_to_md(cursor, table_name):
    try:
        cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 50;')
        rows = cursor.fetchall()
        if not rows:
            return f"### {table_name}\n*Table is empty.*\n\n"
        
        columns = [desc[0] for desc in cursor.description]
        
        md = f"### {table_name.capitalize()}\n"
        md += "| " + " | ".join(columns) + " |\n"
        md += "| " + " | ".join(["---"] * len(columns)) + " |\n"
        for row in rows:
            md += "| " + " | ".join([str(v) for v in row]) + " |\n"
        return md + "\n"
    except Exception as e:
        return f"### {table_name}\nError reading table: {e}\n\n"

def main():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="omniquery",
        password="omniquery123",
        dbname="omniquery_demo"
    )
    cursor = conn.cursor()
    
    output = "# Database Dump (`omniquery_demo`)\n\n"
    output += "Below is the exact data currently saved inside your local PostgreSQL database.\n\n"
    
    tables = ["departments", "employees"]
    for t in tables:
        output += dump_table_to_md(cursor, t)
        
    cursor.close()
    conn.close()
    
    with open("C:/Users/User/.gemini/antigravity/brain/de396f52-1e25-4aab-8aed-3bcc10e21e99/database_dump.md", "w") as f:
        f.write(output)

if __name__ == "__main__":
    main()
