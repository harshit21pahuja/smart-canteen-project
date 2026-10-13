import os
import sqlite3
from dotenv import load_dotenv

# Load local .env if available
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(BASE_DIR, "database.db")
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class SmartRow(dict):
    """Hybrid row that supports both dict key access (row['name']) and index access (row[0])"""
    def __init__(self, d):
        super().__init__(d)
        self._val_list = list(d.values())

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._val_list[key]
        return super().__getitem__(key)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"'SmartRow' object has no attribute '{name}'")


class PostgresCursorWrapper:
    def __init__(self, cur):
        self.cur = cur

    def execute(self, query, params=None):
        # Convert SQLite style ? placeholders to Postgres %s placeholders
        pg_query = query.replace("?", "%s")
        if params is not None:
            self.cur.execute(pg_query, params)
        else:
            self.cur.execute(pg_query)
        return self

    def fetchone(self):
        row = self.cur.fetchone()
        if row is None:
            return None
        return SmartRow(dict(row))

    def fetchall(self):
        rows = self.cur.fetchall()
        return [SmartRow(dict(r)) for r in rows]

    @property
    def rowcount(self):
        return self.cur.rowcount


class PostgresConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self):
        return PostgresCursorWrapper(self.conn.cursor(cursor_factory=RealDictCursor))

    def execute(self, query, params=None):
        cur = self.cursor()
        cur.execute(query, params)
        return cur

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def is_postgres():
    return bool(DATABASE_URL and (DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://"))) and PSYCOPG2_AVAILABLE


def get_db():
    if is_postgres():
        conn = psycopg2.connect(DATABASE_URL)
        return PostgresConnectionWrapper(conn)
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def init_db():
    """Initializes schema and seed data on either PostgreSQL or SQLite"""
    conn = get_db()
    cur = conn.cursor()
    pg = is_postgres()

    id_type = "SERIAL PRIMARY KEY" if pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    real_type = "DOUBLE PRECISION" if pg else "REAL"

    # Core Tables
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS users (
        id {id_type},
        name TEXT,
        roll TEXT UNIQUE,
        phone TEXT,
        email TEXT,
        program TEXT,
        course TEXT,
        specialization TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS meals (
        roll TEXT PRIMARY KEY,
        breakfast TEXT,
        lunch TEXT,
        snacks TEXT,
        dinner TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS menu (
        date TEXT PRIMARY KEY,
        breakfast TEXT,
        lunch TEXT,
        snacks TEXT,
        dinner TEXT
    );
    """)

    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS student_suggestions (
        id {id_type},
        roll TEXT,
        suggestion TEXT,
        date TEXT
    );
    """)

    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS historical_meals (
        id {id_type},
        date TEXT,
        breakfast_count INTEGER,
        lunch_count INTEGER,
        snacks_count INTEGER,
        dinner_count INTEGER
    );
    """)

    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS waste_logs (
        id {id_type},
        date TEXT,
        meal_type TEXT,
        waste_percentage {real_type}
    );
    """)

    # Enable Row Level Security (RLS) on PostgreSQL tables to secure public API access
    if pg:
        for tbl in ["users", "meals", "menu", "student_suggestions", "historical_meals", "waste_logs"]:
            cur.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;")

    conn.commit()

    # Seed default menu
    cur.execute("SELECT COUNT(*) FROM menu")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO menu (date, breakfast, lunch, snacks, dinner)
        VALUES (?, ?, ?, ?, ?)
        """, ('today', 'Aloo Paratha & Curd', 'Rajma Chawal & Salad', 'Samosa & Chai', 'Paneer Butter Masala & Roti'))
        conn.commit()

    # Seed test student
    cur.execute("SELECT COUNT(*) FROM users WHERE roll = ?", ('101',))
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO users (name, roll, phone, email, program, course, specialization)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('Test Student', '101', '9876543210', 'student@example.com', 'B.Tech', 'CSE', 'AI & ML'))
        conn.commit()

    # Seed initial test booking
    cur.execute("SELECT COUNT(*) FROM meals WHERE roll = ?", ('101',))
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO meals (roll, breakfast, lunch, snacks, dinner)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(roll) DO UPDATE SET breakfast='Yes', lunch='No', snacks='Yes', dinner='Yes'
        """, ('101', 'Yes', 'No', 'Yes', 'Yes'))
        conn.commit()

    # Seed historical meals if empty
    cur.execute("SELECT COUNT(*) FROM historical_meals")
    if cur.fetchone()[0] == 0:
        import datetime
        import random
        for i in range(30):
            d = (datetime.date.today() - datetime.timedelta(days=30-i)).isoformat()
            cur.execute("""
            INSERT INTO historical_meals (date, breakfast_count, lunch_count, snacks_count, dinner_count)
            VALUES (?, ?, ?, ?, ?)
            """, (d, random.randint(30, 80), random.randint(50, 100), random.randint(20, 60), random.randint(40, 90)))
        conn.commit()

    # Seed waste logs if empty
    cur.execute("SELECT COUNT(*) FROM waste_logs")
    if cur.fetchone()[0] == 0:
        import datetime
        import random
        for i in range(15):
            d = (datetime.date.today() - datetime.timedelta(days=15-i)).isoformat()
            cur.execute("""
            INSERT INTO waste_logs (date, meal_type, waste_percentage)
            VALUES (?, ?, ?)
            """, (d, random.choice(["breakfast", "lunch", "snacks", "dinner"]), round(random.uniform(5.0, 35.0), 1)))
        conn.commit()

    conn.close()
    backend_name = "Cloud PostgreSQL (Supabase)" if pg else "Local SQLite"
    print(f"[DATABASE] Connected & synchronized with: {backend_name}")
