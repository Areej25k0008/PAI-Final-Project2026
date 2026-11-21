# classifier.py  (written by Wajeeh)
# Predicts the category of an expense from its text (for example "kfc lunch" -> Food).
# There are two classifiers: keyword rules and TF-IDF + Naive Bayes.
# Both have predict() and evaluate(), so the menu can use any of them.

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

from storage import LABELLED_FILE


# ------------------------------------------------------------
# Part 1: text cleaning (our own code, no library)
# ------------------------------------------------------------

PUNCTUATION = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

# very common words that do not help to find the category
STOP_WORDS = {"a", "an", "the", "and", "or", "of", "to", "for", "at", "in", "on",
              "with", "from", "my", "me", "i", "is", "it", "was", "by", "some",
              "new", "after", "back"}


def clean_text(text):
    # lowercase and change every punctuation mark to a space
    text = text.lower()
    letters = [" " if ch in PUNCTUATION else ch for ch in text]     # list comprehension
    return "".join(letters)


def get_words(text):
    # cleans the text, splits it into words and removes stop words and numbers
    words = clean_text(text).split()
    return [w for w in words if w not in STOP_WORDS and not w.isdigit()]


# ------------------------------------------------------------
# Part 2: keyword rules, a dictionary of category -> set of words
# ------------------------------------------------------------

KEYWORDS = {
    "Food": {"lunch", "dinner", "breakfast", "chai", "tea", "coffee", "kfc",
             "burger", "pizza", "biryani", "snacks", "grocery", "groceries",
             "juice", "restaurant", "cafe", "canteen", "bakery", "meal",
             "samosa", "karahi", "ice", "cream", "food", "paratha", "sandwich"},
    "Transport": {"uber", "careem", "rickshaw", "taxi", "bus", "petrol", "fuel",
                  "ride", "fare", "parking", "cab", "indrive", "ticket", "toll",
                  "metro", "commute", "bike", "train"},
    "Bills": {"bill", "bills", "electricity", "gas", "water", "internet", "wifi",
              "rent", "topup", "top", "load", "package", "recharge", "mobile",
              "ptcl", "broadband", "utility", "maintenance"},
    "Shopping": {"shoes", "shirt", "jeans", "daraz", "bag", "backpack", "clothes",
                 "jacket", "perfume", "watch", "sneakers", "wallet", "gift",
                 "shopping", "earphones", "sunglasses", "makeup"},
    "Fun": {"cinema", "movie", "netflix", "spotify", "game", "games", "gaming",
            "concert", "bowling", "party", "trip", "beach", "picnic", "karaoke",
            "arcade", "pubg", "steam", "youtube"},
    "Education": {"book", "textbook", "tuition", "fee", "semester", "course",
                  "udemy", "coursera", "notebooks", "pens", "stationery",
                  "photocopies", "printing", "exam", "library", "lab", "calculator"},
}


# ------------------------------------------------------------
# Part 3: the classifier classes (inheritance + polymorphism)
# ------------------------------------------------------------

class Classifier:
    # parent class: evaluate() is written here once and both children use it

    name = "classifier"

    def predict(self, text):
        # each child class writes its own predict()
        raise NotImplementedError("predict() must be written in the child class.")

    def evaluate(self, test_data):
        # test_data is a list of (text, real_category) tuples
        real = []
        predicted = []
        for text, category in test_data:
            real.append(category)
            predicted.append(self.predict(text))    # works for any child class

        labels = sorted(set(real) | set(predicted))     # set = every category only once
        return {
            "accuracy": accuracy_score(real, predicted),
            "labels": labels,
            "confusion_matrix": confusion_matrix(real, predicted, labels=labels),
        }


class KeywordClassifier(Classifier):
    name = "Keyword rules"

    def predict(self, text):
        words = set(get_words(text))
        best_category = "Other"         # used when no keyword matches
        best_score = 0
        for category, rule_words in KEYWORDS.items():
            score = len(words & rule_words)     # how many words are in common
            if score > best_score:
                best_score = score
                best_category = category
        return best_category


class NaiveBayesClassifier(Classifier):
    name = "TF-IDF + Naive Bayes"

    def __init__(self):
        self.vectoriser = TfidfVectorizer()     # changes text into numbers
        self.model = MultinomialNB()
        self.is_trained = False

    def fit(self, train_data):
        # train on a list of (text, category) tuples
        texts = []
        labels = []
        for text, category in train_data:
            texts.append(" ".join(get_words(text)))     # use our own cleaning first
            labels.append(category)
        numbers = self.vectoriser.fit_transform(texts)
        self.model.fit(numbers, labels)
        self.is_trained = True

    def predict(self, text):
        if not self.is_trained:
            raise RuntimeError("Call fit() before predict().")
        numbers = self.vectoriser.transform([" ".join(get_words(text))])
        return str(self.model.predict(numbers)[0])


# ------------------------------------------------------------
# Part 4: training data, splitting and comparing
# ------------------------------------------------------------

def load_labelled_data():
    # reads expenses_labelled.csv and gives a list of (text, category) tuples
    df = pd.read_csv(LABELLED_FILE)
    df = df.dropna(subset=["text", "category"])
    return list(zip(df["text"], df["category"]))


def split_data(data):
    # 75% for training, 25% for testing. random_state makes the split the same every time
    labels = [category for text, category in data]
    train, test = train_test_split(data, test_size=0.25, random_state=42, stratify=labels)
    return train, test


def build_classifiers():
    # trains the Naive Bayes model and gives (dictionary of classifiers, test data)
    data = load_labelled_data()
    train, test = split_data(data)
    naive_bayes = NaiveBayesClassifier()
    naive_bayes.fit(train)
    classifiers = {"keyword": KeywordClassifier(), "naive_bayes": naive_bayes}
    return classifiers, test


def compare_classifiers(classifiers, test_data):
    # both classifiers are tested on the same unseen test data
    results = {}
    for key, classifier in classifiers.items():
        results[key] = classifier.evaluate(test_data)
    return results
