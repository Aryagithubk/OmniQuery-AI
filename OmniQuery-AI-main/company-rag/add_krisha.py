import psycopg2
import hashlib

conn = psycopg2.connect(
    host="localhost", port=5432,
    user="omniquery", password="omniquery123",
    dbname="omniquery_demo"
)
conn.autocommit = True
cur = conn.cursor()

pw = hashlib.sha256("krishapassword".encode()).hexdigest()

# Check if already exists (from failed earlier test)
cur.execute("SELECT id FROM employees WHERE email = 'krisha.arya@company.com'")
existing = cur.fetchone()

if existing:
    cur.execute("UPDATE employees SET role = 'superadmin' WHERE email = 'krisha.arya@company.com'")
    print("Krisha already existed, updated role to superadmin.")
else:
    cur.execute(
        """INSERT INTO employees 
           (first_name, last_name, email, department_id, job_title, salary, hire_date, is_active, password_hash, role)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        ("Krisha", "Arya", "krisha.arya@company.com", 1, "AI Architect", 180000, "2024-04-13", True, pw, "superadmin")
    )
    print("Krisha Arya inserted successfully!")

# Verify
cur.execute("SELECT id, first_name, last_name, email, job_title, salary, role FROM employees WHERE email = 'krisha.arya@company.com'")
row = cur.fetchone()
print(f"\nVerification:")
print(f"  ID:        {row[0]}")
print(f"  Name:      {row[1]} {row[2]}")
print(f"  Email:     {row[3]}")
print(f"  Job Title: {row[4]}")
print(f"  Salary:    ${row[5]:,.2f}")
print(f"  Role:      {row[6]}")

cur.close()
conn.close()
