from voice_bot.voice_listener import listen_to_user
from voice_bot.nlp_handler import handle_query
import pyttsx3
import os
from datetime import datetime

# ==== Text-to-Speech Setup ====
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1)

# Select female voice
voices = engine.getProperty('voices')
for voice in voices:
    if "female" in voice.name.lower() or "zira" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        print(f"🔊 Using voice: {voice.name}")
        break

def speak(text):
    engine.say(text)
    engine.runAndWait()

# ==== Logging ====
log_path = "logs/chat_log.txt"
os.makedirs(os.path.dirname(log_path), exist_ok=True)

def log_interaction(user, bot):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] 👤 You: {user}\n")
        log_file.write(f"[{timestamp}] 🤖 Bot: {bot}\n\n")

# ==== Main Loop ====
def chatbot_loop():
    print("🎤 Voice chatbot initialized. Say something, or type 'text' to enter manually...")
    print("📝 Type or say 'exit' to quit, or say 'repeat' to hear the last response.\n")

    last_response = ""

    while True:
        query = listen_to_user()

        if not query or "text" in query.lower():
            query = input("⌨️ Type your query: ")

        query = query.strip().lower()

        if not query:
            print("⚠️ No input detected. Try again.")
            continue

        print("👤 You said:", query)

        if query in ["exit", "quit", "bye", "goodbye"]:
            farewell = "Goodbye! Have a great day."
            print("🤖 Bot:", farewell)
            speak(farewell)
            break

        if "repeat" in query:
            print("🔁 Repeating last response:")
            print("🤖 Bot:", last_response)
            speak(last_response)
            continue

        # Get response from bot
        response = handle_query(query)
        print("🤖 Bot:", response)
        speak(response)
        last_response = response

        # Save to log
        log_interaction(query, response)

if __name__ == "__main__":
    chatbot_loop()
