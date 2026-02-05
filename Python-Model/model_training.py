# model_training.py
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Sample training data
texts = ["I love Python", "Python is great", "I hate bugs", "Debugging is annoying"]
labels = [1, 1, 0, 0]  # 1 = positive, 0 = negative

# Convert text to numerical features
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(texts)

# Train a Naive Bayes classifier
model = MultinomialNB()
model.fit(X, labels)

# Save model and vectorizer
joblib.dump(model, "sentiment_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("Model trained and saved successfully!")