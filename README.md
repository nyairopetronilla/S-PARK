# S-PARK
# 🚗 AIoT-Based Car Parking System

## 📘 Project Summary

This project was an AIoT-based Smart Parking System aimed at solving the parking congestion problem at a University. By integrating **Arduino-powered sensors**, **real-time monitoring**, and **AI-driven features** (like voice commands and predictive analytics), the system offered a smarter, safer, and more efficient way to manage university parking spaces.

## 🎯 Objectives
- 🧠 Use AI & IoT to monitor parking occupancy and entry/exit in real-time.
- 📉 Reduce time spent searching for parking spots.
- 🎤 Implement a voice-enabled assistant to support security personnel.
- 📊 Analyze parking patterns and generate smart reports.
- 🔒 Enhance security with real-time slot status and alerts.

## 🧱 Tech Stack

### Hardware
- **Arduino UNO R3**
- **Infrared (IR) Sensors** for slot & entry/exit detection
- **Servo Motors** for automated barrier control
- **I2C LCD Display** for real-time on-site updates

### Software
- **Arduino IDE** – microcontroller programming
- **Python + Flask** – backend and RESTful API
- **MySQL** – database for all system data
- **HTML/CSS/JavaScript + AJAX** – responsive web interface
- **NLTK + spaCy** – voice assistant NLP
- **TensorFlow** – predictive analytics on usage patterns
- **pySerial** – Arduino ↔ Python communication

## 🔧 Features

- 🔐 Role-based access control (Admin/Security)
- 🚦 Real-time parking slot availability
- 📋 Vehicle registration & slot assignment
- 🗣️ AI-powered chatbot for voice queries
- 📈 Usage analytics (charts, stats, predictions)
- 🧾 Exportable reports & PDF generation
- 🌐 Web UI + LCD interface sync

## 🧪 Testing & Validation

- Unit, integration, and system testing using a V-model.
- Voice command testing using confusion matrix.

## 📂 Project Structure
AIoT-Smart-Parking-System/
│
├── Automated_Parking.ino           # Arduino code for IR sensors, LCD, and servo motor control
│
├── backend/                        # Flask-based backend logic
│   ├── app.py                      # Main Flask application with routes and server setup
│   ├── lcd_serial_display.py      # Reads serial data from Arduino and parses parking info
│   ├── reports_handler.py         # Inserts parsed data into the MySQL reports table
│   └── db_config.py               # Centralized DB connection configuration
│
├── voice_bot/                      # AI chatbot functionality
│   └── nlp_handler.py             # Handles voice commands using NLP (NLTK + spaCy)
│
├── templates/                      # HTML templates for the web app
│   ├── dashboard.html             # Real-time dashboard interface
│   ├── reports.html               # Historical reports and analytics
│   ├── register.html              # User registration page
│   └── layout.html                # Shared base layout for templating
│
├── static/                         # Frontend static assets
│   ├── css/                       # Tailwind and custom styles
│   ├── js/                        # JavaScript for live updates, DataTables, and interactivity
│   └── images/                    # Icons, logos, UI illustrations
│
├── database/
│   └── smart_parking_system.sql   # SQL schema for users, reports, vehicles, and more
│
├── requirements.txt               # Python dependencies for setting up the backend
├── README.md                      # Project documentation (this file)
└── run_instructions.md            # Setup and usage instructions for the system


## 🔮 Future Work Examples

- Add a mobile app with push notifications.
- Integrate license plate recognition with camera feeds.
- Include solar-powered sensors for sustainability.
- Enable digital payments for visitor parking.
- Improve voice command recognition using transformer models.

> *“No more circling the parking lot – now we park smart.”*



