import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def update_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Core application tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        roll TEXT UNIQUE,
        phone TEXT,
        email TEXT,
        program TEXT,
        course TEXT,
        specialization TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS meals (
        roll TEXT PRIMARY KEY,
        breakfast TEXT,
        lunch TEXT,
        snacks TEXT,
        dinner TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS menu (
        date TEXT PRIMARY KEY,
        breakfast TEXT,
        lunch TEXT,
        snacks TEXT,
        dinner TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS student_suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll TEXT,
        suggestion TEXT,
        date TEXT
    )
    """)
    
    # Track historical meals for AI training
    cur.execute("""
    CREATE TABLE IF NOT EXISTS historical_meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        breakfast_count INTEGER,
        lunch_count INTEGER,
        snacks_count INTEGER,
        dinner_count INTEGER
    )
    """)
    
    # Track food waste detected by CV
    cur.execute("""
    CREATE TABLE IF NOT EXISTS waste_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        meal_type TEXT,
        waste_percentage REAL
    )
    """)
    
    # Insert some dummy historical data if empty
    cur.execute("SELECT COUNT(*) FROM historical_meals")
    if cur.fetchone()[0] == 0:
        import datetime
        import random
        # Generate last 30 days of dummy data
        for i in range(30):
            d = (datetime.date.today() - datetime.timedelta(days=30-i)).isoformat()
            cur.execute("""
            INSERT INTO historical_meals (date, breakfast_count, lunch_count, snacks_count, dinner_count)
            VALUES (?, ?, ?, ?, ?)
            """, (d, random.randint(30, 80), random.randint(50, 100), random.randint(20, 60), random.randint(40, 90)))
            
    # Insert some dummy waste logs if empty
    cur.execute("SELECT COUNT(*) FROM waste_logs")
    if cur.fetchone()[0] == 0:
        import datetime
        import random
        for i in range(15):
            d = (datetime.date.today() - datetime.timedelta(days=15-i)).isoformat()
            cur.execute("""
            INSERT INTO waste_logs (date, meal_type, waste_percentage)
            VALUES (?, ?, ?)
            """, (d, random.choice(["breakfast", "lunch", "snacks", "dinner"]), random.uniform(5.0, 45.0)))
            
    # Insert default menu if empty
    cur.execute("SELECT COUNT(*) FROM menu")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO menu (date, breakfast, lunch, snacks, dinner)
        VALUES ('today', 'Aloo Paratha & Curd', 'Rajma Chawal & Salad', 'Samosa & Chai', 'Paneer Butter Masala & Roti')
        """)

    # Insert a sample student for quick testing if empty
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO users (name, roll, phone, email, program, course, specialization)
        VALUES ('Test Student', '101', '9876543210', 'student@example.com', 'B.Tech', 'CSE', 'AI & ML')
        """)

    conn.commit()
    conn.close()
    print("Database synced for AI!")

if __name__ == "__main__":
    update_db()
