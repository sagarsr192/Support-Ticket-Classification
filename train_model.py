import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

from preprocess import clean_text

# load dataset
data = pd.read_csv("data/tickets.csv")

# clean text
data["clean_text"] = data["tickets_text"].apply(clean_text)

# Drop rows with missing category
data = data.dropna(subset=['category'])

X = data["clean_text"]
y = data["category"]

# vectorization
vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)

# split data
X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42
)

# model
model = LogisticRegression()
model.fit(X_train, y_train)

# evaluation
predictions = model.predict(X_test)

print("Model Evaluation")
print(classification_report(y_test, predictions))

# save model
pickle.dump(model, open("models/ticket_model.pkl", "wb"))
pickle.dump(vectorizer, open("models/vectorizer.pkl", "wb"))

print("Model saved successfully")