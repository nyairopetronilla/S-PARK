from flask import Blueprint, render_template, request, redirect, flash, url_for
from db_config import get_db_connection
from datetime import datetime
import pymysql

reservation_bp = Blueprint("reservation_bp", __name__)

@reservation_bp.route("/admin/reservations", methods=["GET", "POST"])
def manage_reservations():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        slot_id = request.form["slot_id"]
        vehicle_id = request.form["vehicle_id"]
        expires_at = request.form["expires_at"]

        # Use the admin's username from the session
        reserved_by = "admin"  # or session["username"] if stored

        cursor.execute("""
            INSERT INTO reservations (slot_id, vehicle_id, reserved_by, reserved_at, expires_at, fulfilled)
            VALUES (%s, %s, %s, NOW(), %s, 0)
        """, (slot_id, vehicle_id, reserved_by, expires_at))
        conn.commit()
        flash("✅ Reservation created successfully.", "success")
        return redirect(url_for('reservation_bp.manage_reservations'))


    # Fetch reservations with vehicle info
    cursor.execute("""
        SELECT r.*, v.registration_plate, v.brand, v.model, v.owner_name
        FROM reservations r
        LEFT JOIN vehicles v ON r.vehicle_id = v.vehicle_id
        ORDER BY r.reserved_at DESC
    """)


    reservations = cursor.fetchall()

    # Get all users
    cursor.execute("SELECT user_id, username FROM users")
    users = cursor.fetchall()

    # Get all vehicles
    cursor.execute("SELECT vehicle_id, registration_plate, brand, model FROM vehicles")
    vehicles = cursor.fetchall()

    conn.close()
    return render_template(
        "reservations.html",
        reservations=reservations,
        users=users,
        vehicles=vehicles,
        now=datetime.now
    )

@reservation_bp.route("/admin/reservations/delete/<int:reservation_id>")
def delete_reservation(reservation_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservations WHERE reservation_id = %s", (reservation_id,))
    conn.commit()
    conn.close()
    flash("❌ Reservation deleted.", "success")
    return redirect(url_for('reservation_bp.manage_reservations'))


@reservation_bp.route("/admin/reservations/edit/<int:reservation_id>", methods=["GET", "POST"])
def edit_reservation(reservation_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        slot_id = request.form["slot_id"]
        vehicle_id = request.form["vehicle_id"]
        expires_at = request.form["expires_at"]
        fulfilled = int(request.form["fulfilled"])

        cursor.execute("""
            UPDATE reservations
            SET slot_id = %s, vehicle_id = %s, expires_at = %s, fulfilled = %s
            WHERE reservation_id = %s
        """, (slot_id, vehicle_id, expires_at, fulfilled, reservation_id))
        conn.commit()
        conn.close()

        flash("✅ Reservation updated successfully.", "success")
        return redirect(url_for('reservation_bp.manage_reservations'))

    # GET: Load existing reservation details
    cursor.execute("SELECT * FROM reservations WHERE reservation_id = %s", (reservation_id,))
    reservation = cursor.fetchone()

    cursor.execute("SELECT vehicle_id, registration_plate, brand, model FROM vehicles")
    vehicles = cursor.fetchall()

    conn.close()
    return render_template("edit_reservation.html", reservation=reservation, vehicles=vehicles)

