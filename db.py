import sqlite3

DB_FILE = "pr_review.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS pr_state (
            pr_number INTEGER PRIMARY KEY,
            last_step INTEGER,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_state(pr_number):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT last_step, status FROM pr_state WHERE pr_number=?", (pr_number,))
    row = c.fetchone()
    conn.close()
    return row if row else (0, "running")

def update_state(pr_number, step, status="running"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO pr_state (pr_number, last_step, status)
        VALUES (?, ?, ?)
        ON CONFLICT(pr_number) DO UPDATE SET last_step=?, status=?
    """, (pr_number, step, status, step, status))
    conn.commit()
    conn.close()
