import speech_recognition as sr

def listen_to_user():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I didn’t understand that."
    except sr.RequestError:
        return "Speech recognition service is down."
