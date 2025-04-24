# reports_handler.py

import smtplib
from email.mime.text import MIMEText
from db_config import get_db_connection

def insert_report(user_id, device_id, available_slots, slot1, slot2, slot3, slot4, slot5, slot6):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO reports (user_id, device_id, available_slots,
                                     slot1, slot2, slot3, slot4, slot5, slot6)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, device_id, available_slots, slot1, slot2, slot3, slot4, slot5, slot6))
        conn.commit()
        print("✅ Report inserted.")
    except Exception as e:
        print("❌ Failed to insert report:", e)


def send_report_email(recipient):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports ORDER BY created_at DESC LIMIT 10")
    reports = cursor.fetchall()

    body = "<h3>Recent Reports</h3><table border='1'>"
    body += "<tr><th>Timestamp</th><th>Available</th><th>Slot 1-6</th></tr>"
    for r in reports:
        body += f"<tr><td>{r['created_at']}</td><td>{r['available_slots']}</td>"
        slots = "".join(["🚗" if r[f"slot{i+1}"] else "✅" for i in range(6)])
        body += f"<td>{slots}</td></tr>"
    body += "</table>"

    msg = MIMEText(body, "html")
    msg["Subject"] = "Strathmore Parking Reports"
    msg["From"] = "you@example.com"
    msg["To"] = recipient

    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login("you@example.com", "yourpassword")
        server.sendmail(msg["From"], [recipient], msg.as_string())

