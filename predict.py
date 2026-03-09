import pickle
from preprocess import clean_text

model = pickle.load(open("models/ticket_model.pkl", "rb"))
vectorizer = pickle.load(open("models/vectorizer.pkl", "rb"))

def predict_ticket(text):

    cleaned = clean_text(text)
    vec = vectorizer.transform([cleaned])

    category = model.predict(vec)[0]

    if category == "Technical":
        priority = "High"
    elif category == "Billing":
        priority = "Medium"
    else:
        priority = "Low"

    return category, priority


if __name__ == "__main__":

    ticket = input("Enter support ticket: ")

    category, priority = predict_ticket(ticket)

    print("Category:", category)
    print("Priority:", priority)