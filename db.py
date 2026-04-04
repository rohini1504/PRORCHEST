import sqlite3

DB_FILE = "pr_review.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # state table
    c.execute("""
        CREATE TABLE IF NOT EXISTS pr_state (
            pr_number INTEGER PRIMARY KEY,
            last_step INTEGER,
            status TEXT
        )
    """)

    # outputs table
    c.execute("""
        CREATE TABLE IF NOT EXISTS pr_outputs (
            pr_number INTEGER,
            step TEXT,
            content TEXT,
            PRIMARY KEY (pr_number, step)
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
        ON CONFLICT(pr_number)
        DO UPDATE SET last_step=?, status=?
    """, (pr_number, step, status, step, status))

    conn.commit()
    conn.close()


# 🔥 THIS IS WHAT YOU WERE MISSING
def save_output(pr_number, step, content):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        INSERT INTO pr_outputs (pr_number, step, content)
        VALUES (?, ?, ?)
        ON CONFLICT(pr_number, step)
        DO UPDATE SET content=excluded.content
    """, (pr_number, step, content))

    conn.commit()
    conn.close()


def get_all_outputs(pr_number):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        SELECT step, content FROM pr_outputs
        WHERE pr_number=?
    """, (pr_number,))

    rows = c.fetchall()
    conn.close()

    return {step: content for step, content in rows}
