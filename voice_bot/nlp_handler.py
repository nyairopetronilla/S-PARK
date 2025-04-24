import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from voice_bot.responses import get_response

# Ensure NLTK resources are available
nltk.download('stopwords')
nltk.download('punkt')

# Load model and vectorizer
with open("model/sps_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("model/sps_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# Preprocessing
stop_words = set(stopwords.words("english"))

def preprocess(text):
    text = text.lower()  # Normalize case
    text = re.sub(r"[^a-zA-Z\s]", "", text)  # Remove punctuation/numbers
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

from shared_state import latest_data

def handle_query(query, return_intent=False):
    cleaned = preprocess(query)
    print(f"🧽 Cleaned input: {cleaned}")

    if not cleaned.strip():
        return "Sorry, I didn’t understand that.", "unknown" if return_intent else "Sorry, I didn’t understand that."

    try:
        X = vectorizer.transform([cleaned])
        label = model.predict(X)[0]
        print(f"🧠 Predicted intent: {label}")

        response = get_response(label, data=latest_data, user_id=2, reserved_by="security1")

        if return_intent:
            return label, response
        return response

    except Exception as e:
        print(f"⚠️ NLP handler error: {e}")
        return "Sorry, I didn’t understand that.", "unknown" if return_intent else "Sorry, I didn’t understand that."
