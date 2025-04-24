import json
from flask import Blueprint, request, redirect, render_template, session, flash
from db_config import get_db_connection
import pymysql


vehicle_bp = Blueprint('vehicle_bp', __name__)

@vehicle_bp.route('/register-vehicle', methods=['GET', 'POST'])
def register_vehicle():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == 'POST':
        user_id = session.get('user_id')
        registration_plate = request.form['registration_plate']
        brand = request.form['brand']
        model = request.form['model']
        color = request.form['color']
        owner_name = request.form['owner_name']
        phone_number = request.form['phone_number']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vehicles (user_id, owner_name, phone_number, registration_plate, brand, model, color) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, owner_name, phone_number, registration_plate, brand, model, color))
        conn.commit()
        conn.close()

        flash("✅ Vehicle registered successfully.", "success")
        return redirect('/vehicles')

    # ✅ Load car data from JSON
    with open("static/data/car_data.json", "r") as f:
        car_data = json.load(f)

    return render_template("register_vehicle.html", car_data=car_data)

@vehicle_bp.route('/vehicles')
def vehicle_list():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if session.get("role") == "admin":
        # Admin sees all
        cursor.execute("SELECT * FROM vehicles ORDER BY vehicle_id DESC")
    else:
        # Users only see their own
        user_id = session.get("user_id")
        cursor.execute("SELECT * FROM vehicles WHERE user_id = %s ORDER BY vehicle_id DESC", (user_id,))

    vehicles = cursor.fetchall()
    conn.close()

    return render_template("vehicles.html", vehicles=vehicles)


@vehicle_bp.route('/admin/edit-vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
def edit_vehicle(vehicle_id):
    if session.get("role") != "admin":
        return redirect("/dashboard")

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        owner_name = request.form['owner_name']
        phone_number = request.form['phone_number']
        registration_plate = request.form['registration_plate']
        brand = request.form['brand']
        model = request.form['model']
        color = request.form['color']

        cursor.execute("""
            UPDATE vehicles
            SET owner_name=%s, phone_number=%s, registration_plate=%s,
                brand=%s, model=%s, color=%s
            WHERE vehicle_id = %s
        """, (owner_name, phone_number, registration_plate, brand, model, color, vehicle_id))
        conn.commit()
        conn.close()
        flash("✅ Vehicle updated successfully.")
        return redirect("/admin/vehicles")

    cursor.execute("SELECT * FROM vehicles WHERE vehicle_id = %s", (vehicle_id,))
    vehicle = cursor.fetchone()
    conn.close()
    return render_template("edit_vehicle.html", vehicle=vehicle)


@vehicle_bp.route('/admin/delete-vehicle/<int:vehicle_id>')
def delete_vehicle(vehicle_id):
    if session.get("role") != "admin":
        return redirect("/dashboard")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicles WHERE vehicle_id = %s", (vehicle_id,))
    conn.commit()
    conn.close()
    flash("❌ Vehicle deleted successfully.")
    return redirect("/admin/vehicles")


@vehicle_bp.route('/admin/print-vehicle/<int:vehicle_id>')
def print_vehicle(vehicle_id):
    if session.get("role") != "admin":
        return redirect("/dashboard")

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM vehicles WHERE vehicle_id = %s", (vehicle_id,))
    vehicle = cursor.fetchone()
    conn.close()
    return render_template("print_vehicle.html", vehicle=vehicle)

