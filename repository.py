from psycopg.rows import dict_row #plays the role sqlite3.Row did
import psycopg
import os


from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]

# DB_PATH = Path(__file__).parent / "tasks.db"

SEED_TASKS = [
    ("Buy milk", False),
    ("Walk the dog", False),
    ("Read a book", True),
]

def get_db():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def init_db():
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS tasks ("
                    "id SERIAL PRIMARY KEY, "
                    "title TEXT NOT NULL, "
                    "done BOOLEAN NOT NULL DEFAULT FALSE)" # Seed vals are now FALSE/TRUE instead of 0/1
                )
                count = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
                if count == 0:
                    cur.executemany(
                        "INSERT INTO tasks (title, done) VALUES (%s, %s)", SEED_TASKS
                    )
    finally:
        conn.close()

  

