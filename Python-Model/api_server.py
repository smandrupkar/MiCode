# api_server.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

# Load model and vectorizer
model = joblib.load("sentiment_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

app = FastAPI(title="Sentiment Analysis API")

# Request body schema
class TextInput(BaseModel):
    text: str

@app.post("/predict")
def predict_sentiment(input_data: TextInput):
    try:
        # Transform input text
        X = vectorizer.transform([input_data.text])
        prediction = model.predict(X)[0]
        sentiment = "Positive" if prediction == 1 else "Negative"
        return {"sentiment": sentiment}
    except Exception as e:
        return {"error": str(e)}

# Run with: uvicorn api_server:app --reload