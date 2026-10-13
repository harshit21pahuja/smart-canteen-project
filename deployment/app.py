from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "smartcanteen_secret"

import os
from twilio.rest import Client

from ai_models.meal_predictor import predict_tomorrow_meals
from ai_models.waste_detector import analyze_plate_image
from ai_models.menu_recommender import suggest_menu
from ai_models.sentiment_analyzer import analyze_sentiments
# ================= TWILIO CONFIGURATION =================
# Replace these with your actual Twilio API credentials to send real SMS
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "YOUR_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "YOUR_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "YOUR_PHONE_NUMBER")

def send_otp(phone, email, otp):
    print("\n" + "="*40)
    print(">> [SMART CANTEEN] SENDING OTP...")
    print(f">> Phone: {phone}")
    print(f">> Email: {email}")
    print(f">> Your OTP : {otp}")
    print("="*40 + "\n")

    # Send SMS via Twilio
    try:
        if len(phone) == 10 and phone.isdigit():
            phone = "+91" + phone  # Prepend Indian country code if needed
            
        if TWILIO_ACCOUNT_SID not in ["YOUR_ACCOUNT_SID", "your_account_sid_here"]:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"Your Smart Canteen Login OTP is: {otp}",
                from_=TWILIO_PHONE_NUMBER,
                to=phone
            )
            print(f"[OK] SMS successfully sent via Twilio! Message SID: {message.sid}")
        else:
            print("[INFO] Twilio API not configured. Using console-printed OTP for testing.")
    except Exception as e:
        print(f"[ERROR] Failed to send SMS via Twilio: {str(e)}")

from db import get_db, init_db, is_postgres

# Automatically sync database schema & seed data on startup (supports Supabase PostgreSQL & SQLite fallback)
try:
    init_db()
except Exception as e:
    print(f"[INIT] Database sync notice: {e}")


@app.route("/")
def home():
    return redirect(url_for("login"))


# ================= REGISTER =================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        roll = request.form["roll"]
        phone = request.form["phone"]
        email = request.form["email"]
        program = request.form["program"]
        course = request.form["course"]
        specialization = request.form["specialization"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (name,roll,phone,email,program,course,specialization) VALUES (?,?,?,?,?,?,?)",
            (name, roll, phone, email, program, course, specialization)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        roll = request.form["roll"]
        phone = request.form["phone"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE roll=? AND phone=?",
            (roll, phone)
        )

        user = cur.fetchone()

        if user:
            otp = str(random.randint(100000, 999999))
            
            # Send real OTP via Twilio and Email (or terminal if keys missing)
            send_otp(user["phone"], user["email"], otp)

            session["pending_login"] = {
                "name": user["name"],
                "roll": user["roll"],
                "phone": user["phone"],
                "email": user["email"],
                "program": user["program"],
                "course": user["course"],
                "specialization": user["specialization"],
                "otp": otp
            }

            return redirect(url_for("verify_otp"))

        return render_template("login.html", error="Invalid Enrollment or Phone number. If you haven't registered, please create an account below.")

    return render_template("login.html")

# ================= OTP VERIFICATION =================

@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if "pending_login" not in session:
        return redirect(url_for("login"))

    pending = session["pending_login"]
    demo_otp = pending.get("otp") if TWILIO_ACCOUNT_SID in ["YOUR_ACCOUNT_SID", "your_account_sid_here"] else None

    if request.method == "POST":
        user_otp = request.form["otp"]

        if user_otp == pending["otp"]:
            session["name"] = pending["name"]
            session["roll"] = pending["roll"]
            session["phone"] = pending["phone"]
            session["email"] = pending["email"]
            session["program"] = pending["program"]
            session["course"] = pending["course"]
            session["specialization"] = pending["specialization"]
            
            session.pop("pending_login", None)
            return redirect(url_for("profile"))

        return render_template("verify_otp.html", error="Invalid OTP code. Please try again.", demo_otp=demo_otp)

    return render_template("verify_otp.html", demo_otp=demo_otp)


# ================= PROFILE =================

@app.route("/profile")
def profile():

    if "name" not in session:
        return redirect(url_for("login"))
        
    msg = request.args.get("msg")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM meals WHERE roll=?", (session["roll"],))
    existing_booking = cur.fetchone()
    conn.close()

    return render_template(
        "profile.html",
        name=session["name"],
        roll=session["roll"],
        phone=session["phone"],
        email=session.get("email", ""),
        program=session.get("program", ""),
        course=session.get("course", ""),
        specialization=session["specialization"],
        existing_booking=existing_booking,
        msg=msg
    )

# ================= SUBMIT SUGGESTION =================
@app.route("/submit_suggestion", methods=["POST"])
def submit_suggestion():
    if "roll" not in session:
        return redirect(url_for("login"))
        
    suggestion = request.form.get("suggestion")
    if suggestion:
        conn = get_db()
        cur = conn.cursor()
        import datetime
        cur.execute("INSERT INTO student_suggestions (roll, suggestion, date) VALUES (?, ?, ?)",
                   (session["roll"], suggestion, datetime.date.today().isoformat()))
        conn.commit()
        conn.close()
        
    return redirect(url_for("profile", msg="Your suggestion has been submitted successfully!"))


# ================= MEAL BOOKING =================

@app.route("/meal", methods=["GET", "POST"])
def meal():

    if "roll" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    roll = session["roll"]

    # Get today's menu
    cur.execute("SELECT * FROM menu WHERE date=?", ("today",))
    menu = cur.fetchone()

    # Check if student has already booked
    cur.execute("SELECT * FROM meals WHERE roll=?", (roll,))
    existing_booking = cur.fetchone()

    if request.method == "POST":

        breakfast = request.form.get("breakfast", "No")
        lunch = request.form.get("lunch", "No")
        snacks = request.form.get("snacks", "No")
        dinner = request.form.get("dinner", "No")

        is_update = existing_booking is not None

        cur.execute("""
        INSERT INTO meals (roll, breakfast, lunch, snacks, dinner)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(roll) DO UPDATE SET
        breakfast=excluded.breakfast,
        lunch=excluded.lunch,
        snacks=excluded.snacks,
        dinner=excluded.dinner
        """, (roll, breakfast, lunch, snacks, dinner))

        conn.commit()
        conn.close()

        msg = "Your meal booking has been updated successfully!" if is_update else "Your meal has been booked successfully!"
        return redirect(url_for("profile", msg=msg))

    conn.close()

    return render_template("meal.html", menu=menu, existing_booking=existing_booking)


# ================= ADMIN LOGIN =================

@app.route("/admin", methods=["GET","POST"])
def admin():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))

        return render_template("admin_login.html", error="Invalid admin username or password.")

    return render_template("admin_login.html")


# ================= ADMIN DASHBOARD =================

@app.route("/admin_dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect(url_for("admin"))

    conn = get_db()
    cur = conn.cursor()

    breakfast = cur.execute(
        "SELECT COUNT(*) FROM meals WHERE breakfast='Yes'"
    ).fetchone()[0]

    lunch = cur.execute(
        "SELECT COUNT(*) FROM meals WHERE lunch='Yes'"
    ).fetchone()[0]

    snacks = cur.execute(
        "SELECT COUNT(*) FROM meals WHERE snacks='Yes'"
    ).fetchone()[0]

    dinner = cur.execute(
        "SELECT COUNT(*) FROM meals WHERE dinner='Yes'"
    ).fetchone()[0]
    
    suggestions_count = 0
    sentiment_data = None
    try:
        cur.execute("SELECT * FROM student_suggestions")
        suggestions_raw = cur.fetchall()
        suggestions_count = len(suggestions_raw)
        sentiment_data = analyze_sentiments(suggestions_raw)
    except Exception as e:
        pass

    msg = request.args.get("msg")
    conn.close()
    
    # AI Predictions Integration
    try:
        predictions = predict_tomorrow_meals()
    except Exception as e:
        predictions = {"breakfast": 0, "lunch": 0, "snacks": 0, "dinner": 0}

    return render_template(
        "admin_dashboard.html",
        breakfast=breakfast,
        lunch=lunch,
        snacks=snacks,
        dinner=dinner,
        predictions=predictions,
        suggestions_count=suggestions_count,
        sentiment_data=sentiment_data,
        msg=msg
    )


# ================= CANTEEN DEMO SIMULATOR =================

@app.route("/admin_populate_demo")
def admin_populate_demo():
    if "admin" not in session:
        return redirect(url_for("admin"))

    conn = get_db()
    cur = conn.cursor()

    import random
    import datetime

    # Seed 50 students
    for i in range(1, 51):
        r = f"2024CS{100 + i}"
        name = f"Student {i}"
        phone = f"987654{1000 + i}"
        email = f"student{i}@bennett.edu.in"
        cur.execute("""
        INSERT OR IGNORE INTO users (name, roll, phone, email, program, course, specialization)
        VALUES (?, ?, ?, ?, 'B.Tech', 'CSE', 'AI & ML')
        """, (name, r, phone, email))

        # Realistic canteen attendance rates
        b_val = "Yes" if random.random() < 0.78 else ("Maybe" if random.random() < 0.4 else "No")
        l_val = "Yes" if random.random() < 0.90 else ("Maybe" if random.random() < 0.4 else "No")
        s_val = "Yes" if random.random() < 0.65 else ("Maybe" if random.random() < 0.4 else "No")
        d_val = "Yes" if random.random() < 0.82 else ("Maybe" if random.random() < 0.4 else "No")

        cur.execute("""
        INSERT INTO meals (roll, breakfast, lunch, snacks, dinner)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(roll) DO UPDATE SET
        breakfast=excluded.breakfast,
        lunch=excluded.lunch,
        snacks=excluded.snacks,
        dinner=excluded.dinner
        """, (r, b_val, l_val, s_val, d_val))

    # Add realistic student feedback suggestions
    sample_suggestions = [
        ("2024CS101", "The paneer butter masala today was delicious and very fresh!"),
        ("2024CS103", "Please add more fruit options in breakfast."),
        ("2024CS107", "Dal Makhani quality has improved a lot, loved it!"),
        ("2024CS112", "Snacks were slightly oily today, please make it lighter."),
        ("2024CS118", "Great service and fast plate verification at the counter!"),
        ("2024CS124", "The evening masala chai was amazing today."),
        ("2024CS130", "App is very smooth and meal booking saves queue waiting time.")
    ]
    cur.execute("DELETE FROM student_suggestions")
    today_iso = datetime.date.today().isoformat()
    for roll, text in sample_suggestions:
        cur.execute("INSERT INTO student_suggestions (roll, suggestion, date) VALUES (?, ?, ?)",
                    (roll, text, today_iso))

    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard", msg="Canteen traffic loaded: 50 active students with confirmed meal bookings!"))


@app.route("/admin_reset_demo")
def admin_reset_demo():
    if "admin" not in session:
        return redirect(url_for("admin"))

    conn = get_db()
    cur = conn.cursor()

    # Retain only initial test student 101
    cur.execute("DELETE FROM users WHERE roll != '101'")
    cur.execute("DELETE FROM meals WHERE roll != '101'")
    cur.execute("DELETE FROM student_suggestions")

    # Ensure original test student exists
    cur.execute("""
    INSERT OR IGNORE INTO users (name, roll, phone, email, program, course, specialization)
    VALUES ('Test Student', '101', '9876543210', 'student@example.com', 'B.Tech', 'CSE', 'AI & ML')
    """)

    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard", msg="Database has been reset to original state!"))


# ================= ADMIN MENU =================

@app.route("/admin_menu", methods=["GET","POST"])
def admin_menu():

    if "admin" not in session:
        return redirect(url_for("admin"))

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":

        breakfast = request.form["breakfast"]
        lunch = request.form["lunch"]
        snacks = request.form["snacks"]
        dinner = request.form["dinner"]

        today = "today"

        cur.execute("SELECT * FROM menu WHERE date=?", (today,))
        existing = cur.fetchone()

        if existing:

            cur.execute("""
            UPDATE menu
            SET breakfast=?, lunch=?, snacks=?, dinner=?
            WHERE date=?
            """,(breakfast,lunch,snacks,dinner,today))

        else:

            cur.execute("""
            INSERT INTO menu (date, breakfast, lunch, snacks, dinner)
            VALUES (?,?,?,?,?)
            """,(today,breakfast,lunch,snacks,dinner))

        conn.commit()

    cur.execute("SELECT * FROM menu WHERE date=?", ("today",))
    menu = cur.fetchone()

    conn.close()
    
    # AI Suggestions Integration
    try:
        suggestions, reasonings = suggest_menu()
    except Exception as e:
        suggestions, reasonings = {}, {}

    return render_template("admin_menu.html", menu=menu, suggestions=suggestions, reasonings=reasonings)


# ================= AI PLATE SCANNER =================

@app.route("/admin_plate_scanner", methods=["GET","POST"])
def admin_plate_scanner():
    if "admin" not in session:
        return redirect(url_for("admin"))

    waste_result = None
    if request.method == "POST":
        if 'plate_image' in request.files:
            file = request.files['plate_image']
            if file.filename != '':
                waste_result = analyze_plate_image(file)
                # Log waste
                conn = get_db()
                cur = conn.cursor()
                import datetime
                cur.execute("INSERT INTO waste_logs (date, meal_type, waste_percentage) VALUES (?,?,?)", 
                           (datetime.date.today().isoformat(), "general", waste_result))
                conn.commit()
                conn.close()

    return render_template("admin_plate_scanner.html", waste_result=waste_result)


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() in ["true", "1"]
    app.run(host="0.0.0.0", port=port, debug=debug_mode)