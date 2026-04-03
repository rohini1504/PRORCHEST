import sqlite3

conn = sqlite3.connect("review.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS agent_outputs (
    pr_id TEXT,
    agent_name TEXT,
    output TEXT
)
""")
conn.commit()

def clear_outputs(pr_id):
    cursor.execute("DELETE FROM agent_outputs WHERE pr_id=?", (pr_id,))
    conn.commit()

def save_output(pr_id, agent, output):
    cursor.execute(
        "INSERT INTO agent_outputs VALUES (?, ?, ?)",
        (pr_id, agent, output)
    )
    conn.commit()

def get_outputs(pr_id):
    cursor.execute(
        "SELECT agent_name, output FROM agent_outputs WHERE pr_id=?",
        (pr_id,)
    )
    return cursor.fetchall()
