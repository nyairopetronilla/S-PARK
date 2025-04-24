import time
import json
import serial
import pymysql
import datetime
from threading import Thread
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_socketio import SocketIO
from werkzeug.security import check_password_hash, generate_password_hash
from reports_handler import insert_report
from db_config import get_db_connection
from voice_bot.nlp_handler import handle_query


def get_reserved_slots():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  
    cursor.execute("""
        SELECT slot_id FROM reservations
        WHERE fulfilled = FALSE AND expires_at > NOW()
    """)
    reserved = [row["slot_id"] for row in cursor.fetchall()]  
    
    conn.close()
    return reserved



app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "dev-secret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
from shared_state import latest_data

from vehicle_routes import vehicle_bp
app.register_blueprint(vehicle_bp)

from admin_reservations import reservation_bp
app.register_blueprint(reservation_bp)

SERIAL_PORT = "COM11"
BAUD_RATE = 9600
last_insert_time = 0

def serial_reader():
    global last_insert_time, latest_data
    arduino = None

    while not arduino:
        try:
            arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print(f"✅ Connected to {SERIAL_PORT}")
            time.sleep(2)
        except Exception as e:
            print(f"🔁 Retrying Serial Connection on {SERIAL_PORT}... ({e})")
            time.sleep(2)

    while True:
        try:
            if arduino.in_waiting:
                line = arduino.readline().decode("utf-8", errors="ignore").strip()
                print("🟢 Incoming line:", line)

                try:
                    data = json.loads(line)

                    reserved_slots = get_reserved_slots()
                    actual_available = 0

                    for slot in data["slots"]:
                        slot_id = int(slot["id"])
                        is_reserved = slot_id in reserved_slots

                        # ✅ Force override logic
                        if is_reserved:
                            slot["occupied"] = False
                            slot["reserved"] = True
                        else:
                            slot["reserved"] = False

                        if not slot["occupied"] and not slot["reserved"]:
                            actual_available += 1

                    data["available_slots"] = actual_available




                    latest_data.clear()
                    latest_data.update(data)


                    print("✅ Parsed JSON:", data)

                    socketio.emit("update", data)

                    now = time.time()
                    if now - last_insert_time >= 120:
                        last_insert_time = now

                        conn = get_db_connection()
                        cursor = conn.cursor(pymysql.cursors.DictCursor)  # 🧠 Use DictCursor for safe column access

                        try:
                            # 🧠 This is case-sensitive, so double-check location string
                            cursor.execute("SELECT device_id FROM iot_devices WHERE device_id = %s", (data["device_id"],))
                            result = cursor.fetchone()

                            if result and "device_id" in result:
                                numeric_device_id = result["device_id"]
                                # 🔁 Fetch user_id dynamically (fallback to first user)
                                cursor.execute("SELECT user_id FROM users LIMIT 1")
                                user_id = cursor.fetchone()["user_id"]

                                # ✅ Insert the report
                                insert_report(
                                    user_id=user_id,
                                    device_id=numeric_device_id,
                                    available_slots=data["available_slots"],
                                    slot1=data["slots"][0]["occupied"],
                                    slot2=data["slots"][1]["occupied"],
                                    slot3=data["slots"][2]["occupied"],
                                    slot4=data["slots"][3]["occupied"],
                                    slot5=data["slots"][4]["occupied"],
                                    slot6=data["slots"][5]["occupied"]
                                )
                                print("✅ Inserted report to DB.")

                            else:
                                print(f"❌ Unknown device_id '{data['device_id']}' — cannot insert report.")

                        except Exception as e:
                            print("❌ DB Lookup Error:", e)

                        finally:
                            conn.close()




                except json.JSONDecodeError as e:
                    print("⚠️ JSON decode error:", e)
        except serial.SerialException as e:
            print("❌ Serial disconnected:", e)
            arduino = None
            print("🔄 Reconnecting...")

@socketio.on("connect")
def handle_connect():
    print("🟢 Web client connected to Socket.IO")
    socketio.emit("update", latest_data, broadcast=False)


@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return render_template("welcome.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

@app.route("/lcd-data")
def get_lcd_data():
    return jsonify(latest_data)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = {
            "username": request.form["username"],
            "email": request.form["email"],
            "password": generate_password_hash(request.form["password"]),
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "role": "security"
        }

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password, first_name, last_name, role, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
            (data["username"], data["email"], data["password"], data["first_name"], data["last_name"], data["role"])
        )
        conn.commit()

        cursor.execute("SELECT LAST_INSERT_ID() AS user_id")
        user_id = cursor.fetchone()["user_id"]

        session["user_id"] = user_id
        session["username"] = data["username"]
        session["role"] = data["role"]
        flash("✅ Registration successful. Welcome!")

        return redirect("/dashboard")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect("/")

@app.route("/admin/users", methods=["GET", "POST"])
def manage_users():
    if session.get("role") != "admin":
        return redirect("/dashboard")

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        if "password_to_hash" in request.form:
            password = request.form.get("password_to_hash")
            hash_result = generate_password_hash(password)
            cursor.execute("SELECT user_id, username, email, role, created_at FROM users")
            users = cursor.fetchall()
            conn.close()
            return render_template("admin.html", users=users, hash_result=hash_result)
        else:
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            role = request.form.get("role")
            if username and password and role:
                hashed = generate_password_hash(password)
                cursor.execute("INSERT INTO users (username, email, password, role, created_at) VALUES (%s, %s, %s, %s, NOW())", (username, email, hashed, role))
                conn.commit()
                flash("✅ User created successfully.", "success")

    cursor.execute("SELECT user_id, username, email, role, created_at FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template("admin.html", users=users)

@app.route("/admin/hash", methods=["GET"])
def admin_hash_tool():
    return redirect("/admin/users")

@app.route("/admin/delete-user/<int:user_id>")
def delete_user(user_id):
    if session.get("role") != "admin":
        return redirect("/dashboard")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    flash("❌ User deleted.", "success")
    return redirect("/admin/users")

@app.route("/admin/edit-user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if session.get("role") != "admin":
        return redirect("/dashboard")

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        role = request.form["role"]
        new_password = request.form["password"]

        if new_password:
            hashed = generate_password_hash(new_password)
            cursor.execute(
                "UPDATE users SET username = %s, email = %s, role = %s, password = %s WHERE user_id = %s",
                (username, email, role, hashed, user_id)
            )
        else:
            cursor.execute(
                "UPDATE users SET username = %s, email = %s, role = %s WHERE user_id = %s",
                (username, email, role, user_id)
            )

        conn.commit()
        flash("✅ User updated successfully.", "success")
        return redirect("/admin/users")

    cursor.execute("SELECT user_id, username, email, role FROM users WHERE user_id = %s", (user_id,))
    user_to_edit = cursor.fetchone()

    cursor.execute("SELECT user_id, username, email, role, created_at FROM users")
    users = cursor.fetchall()
    conn.close()

    return render_template("admin.html", users=users, edit_user=user_to_edit)



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user.get("password", ""), password):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash(f"✅ Welcome, {username}!", "success")

            # 👉 Redirect based on role
            if user["role"] == "admin":
                return redirect("/admin/dashboard")
            else:
                return redirect("/dashboard")

        flash("❌ Invalid username or password.", "error")

    return render_template("login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect("/dashboard")
    return render_template("admin_dashboard.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        username = request.form["username"]
        new_password = request.form["new_password"]

        if len(new_password) < 5:
            flash("Password must be at least 5 characters.", "error")
            cursor.execute("SELECT username, role FROM users")
            users = cursor.fetchall()
            return render_template("reset_password.html", users=users)

        hashed = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed, username))
        conn.commit()
        flash("Password reset successful.", "success")
        return redirect("/login")

    # GET — show all users
    cursor.execute("SELECT username, role FROM users ORDER BY role, username")
    users = cursor.fetchall()
    return render_template("reset_password.html", users=users)

@app.route("/admin/create-user", methods=["GET", "POST"])
def admin_create_user():
    if session.get("role") != "admin":
        return "Unauthorized", 403

    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password, role, created_at) VALUES (%s, %s, %s, %s, NOW())",
            (username, f"{username}@strathmore.edu", password, role)
        )
        conn.commit()
        flash("User created successfully.")
        return redirect("/admin/create-user")

    return render_template("admin_create_user.html")  # Create a simple form for this


@app.route("/reports")
def reports_page():
    return render_template("reports.html")

@app.route("/api/reports")
def api_reports():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
    rows = cursor.fetchall()

    # Make sure it's returning clean JSON
    for row in rows:
        for key in row:
            if isinstance(row[key], datetime.datetime):
                row[key] = row[key].strftime('%Y-%m-%d %H:%M:%S')

    return jsonify(rows)



@app.route("/api/slot-usage")
def slot_usage():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT slot1, slot2, slot3, slot4, slot5, slot6 FROM reports")
    rows = cursor.fetchall()
    usage = [0] * 6
    for row in rows:
        for i in range(6):
            if row[i]:
                usage[i] += 1
    return jsonify({"labels": [f"Slot {i+1}" for i in range(6)], "data": usage})

@app.route("/api/analytics")
def api_analytics():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Weekly Trends
    cursor.execute("SELECT DAYNAME(created_at) as day, slot1, slot2, slot3, slot4, slot5, slot6 FROM reports")
    rows = cursor.fetchall()
    weekly = {}
    heatmap = {}
    summary = [0] * 6

    for row in rows:
        day = row["day"]
        if day not in weekly:
            weekly[day] = [0] * 6
        for i in range(6):
            if row[f"slot{i+1}"]:
                weekly[day][i] += 1
                summary[i] += 1
        heatmap[day] = heatmap.get(day, 0) + sum(row[f"slot{i+1}"] for i in range(6))

    most_used_slot = summary.index(max(summary)) + 1
    busiest_day = max(heatmap, key=heatmap.get)

    return jsonify({
        "weeklyTrends": [
            {"day": day, **{f"slot{i+1}": slots[i] for i in range(6)}}
            for day, slots in weekly.items()
        ],
        "heatmap": [{"day": day, "usage": usage} for day, usage in heatmap.items()],
        "summary": {
            "most_used": most_used_slot,
            "busiest_day": busiest_day
        }
    })

@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")


@app.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.json
    message = data.get("message", "")
    user_id = 1
    intent, response = handle_query(message, return_intent=True)
    try:
        conn = pymysql.connect(host="localhost", user="root", password="", db="trial")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chatbot_feedback (user_id, message, response, intent) VALUES (%s, %s, %s, %s)", (user_id, message, response, intent))
        conn.commit()
    except Exception as e:
        print("❌ DB Logging Error:", e)
    return jsonify({"response": response})

@app.route("/api/feedback/rate", methods=["POST"])
def rate_feedback():
    data = request.get_json()
    feedback_id = data.get("feedback_id")
    rating = data.get("rating")
    try:
        conn = pymysql.connect(host="localhost", user="root", password="", db="trial")
        cursor = conn.cursor()
        cursor.execute("UPDATE chatbot_feedback SET rating = %s WHERE feedback_id = %s", (rating, feedback_id))
        conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("❌ Rating error:", e)
        return jsonify({"status": "error"})

@app.route("/feedback")
def feedback_page():
    conn = pymysql.connect(host="localhost", user="root", password="", db="trial")
    cursor = conn.cursor()
    cursor.execute("SELECT feedback_id, user_id, message, response, created_at, intent, rating FROM chatbot_feedback ORDER BY created_at DESC")
    feedback_entries = cursor.fetchall()
    conn.close()
    return render_template("feedback.html", feedback=feedback_entries)

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


if __name__ == "__main__":
    app.debug = True
    thread = Thread(target=serial_reader)
    thread.daemon = True
    thread.start()
    socketio.run(app, debug=True, use_reloader=False, host="127.0.0.1", port=5000, allow_unsafe_werkzeug=True)
