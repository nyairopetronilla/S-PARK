from datetime import datetime, timedelta
from db_config import get_db_connection

from shared_state import latest_data
from shared_state import latest_data
slots = latest_data.get("slots", [])


def reserve_slot(user_id=None, reserved_by="security_user"):
    available_slot = next((slot["id"] for slot in slots if not slot.get("occupied")), None)

    if available_slot:
        expires = datetime.now() + timedelta(minutes=10)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reservations (user_id, slot_id, reserved_by, expires_at)
                VALUES (%s, %s, %s, %s)
            """, (user_id, available_slot, reserved_by, expires))
            conn.commit()
            conn.close()

            return f"📝 Slot {available_slot} has been reserved. Please confirm arrival within 10 minutes."
        except Exception as e:
            return f"⚠️ Failed to reserve slot due to: {e}"
    else:
        return "🚫 Sorry, no available slots to reserve right now."

def get_response(intent, data=None, user_id=None, reserved_by="Security"):
    if data is None:
        return "⚠️ Live data not available at the moment."

    slots = data.get("slots", [])
    available = data.get("available_slots", "N/A")

    if intent == "check_availability":
        if isinstance(available, int) and available > 0:
            return f"🚗 There are {available} available parking slot(s). You're good to go!"
        else:
            return "🚫 Sorry, no empty slots available right now. Please check again in a few minutes."

    elif intent == "find_empty_slots":
        empty = [f"Slot {slot['id']}" for slot in slots if not slot.get("occupied")]
        return f"🟢 Empty slots: {', '.join(empty)}" if empty else "🚫 All slots are currently occupied."

    elif intent == "vehicle_status":
        return "🔍 Please visit your vehicle dashboard."

    elif intent == "security_alert":
        return "🚨 Your alert has been forwarded to campus security. Help is on the way!"

    elif intent == "greeting":
        return "👋 Hi there! How can I assist you with parking today?"

    elif intent == "thank_you":
        return "😊 You're welcome! Let me know if you need anything else."

    elif intent == "goodbye":
        return "👋 Goodbye! Drive safe and have a great day."

    elif intent == "reserve_slot":
        return reserve_slot(user_id=user_id, reserved_by=reserved_by)

    return "🤖 I'm not sure how to help with that yet. Could you rephrase your question?"
