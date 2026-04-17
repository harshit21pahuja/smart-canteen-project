import sqlite3

def update_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    
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
            
    conn.commit()
    conn.close()
    print("Database synced for AI!")

if __name__ == "__main__":
    update_db()
