# models.py  (written by Areej)
# This file has the classes of PaisaPal (Entry, Expense, Budget)
# and the code that reads the line the user types (parse_entry).

# the six categories we use in the project
CATEGORIES = ["Food", "Transport", "Bills", "Shopping", "Fun", "Education"]


# ------------------------------------------------------------
# Part 1: Entry and Expense classes (inheritance, polymorphism)
# ------------------------------------------------------------

class Entry:
    # base class for any money record
    def __init__(self, date, description, amount, category="Other"):
        self.date = date
        self.description = description
        self._amount = 0            # the _ means: do not change this directly
        self.set_amount(amount)     # the check for a positive amount is inside set_amount
        self.category = category

    def get_amount(self):
        return self._amount

    def set_amount(self, value):
        # an amount can never be zero or negative
        if value <= 0:
            raise ValueError("Amount must be greater than zero.")
        self._amount = float(value)

    def describe(self):
        # every child class must write its own describe()
        raise NotImplementedError("describe() must be written in the child class.")

    def to_dict(self):
        # we need a dictionary to write the entry in the csv file
        return {
            "date": str(self.date),
            "description": self.description,
            "amount": self._amount,
            "category": self.category,
        }


class Expense(Entry):
    # one spending entry, it inherits everything from Entry

    def describe(self):
        # this replaces describe() of the parent class (polymorphism)
        return f"{self.date} | {self.category:<10} | Rs {self.get_amount():>9,.2f} | {self.description}"

    def is_large(self, limit=1000):
        # True if the expense is limit rupees or more
        return self.get_amount() >= limit


# ------------------------------------------------------------
# Part 2: Budget class (encapsulation)
# ------------------------------------------------------------

class Budget:
    def __init__(self):
        self.__limits = {}          # the two _ make it private, only this class can use it

    def set_limit(self, category, limit):
        if category not in CATEGORIES:
            raise ValueError("Unknown category: " + category)
        if limit <= 0:
            raise ValueError("Limit must be greater than zero.")
        self.__limits[category] = float(limit)

    def get_limit(self, category):
        return self.__limits.get(category)      # None if no limit was set

    def limits(self):
        return dict(self.__limits)              # a copy, so nobody can change the original

    def check(self, category, total):
        # True if the total is more than the limit of that category
        limit = self.get_limit(category)
        return limit is not None and total > limit

    def warnings(self, summary):
        # summary is a dictionary like {"Food": 5000}
        # we make a warning message for every category that is over its limit
        messages = []
        for category, total in summary.items():
            if self.check(category, total):
                limit = self.get_limit(category)
                messages.append(f"WARNING: {category} spending Rs {total:,.0f} is over the "
                                f"budget of Rs {limit:,.0f} (by Rs {total - limit:,.0f}).")
        return messages


# ------------------------------------------------------------
# Part 3: reading what the user types (the parser)
# ------------------------------------------------------------

class InvalidEntryError(Exception):
    # our own error, we raise it when the typed line is not good
    pass


def to_number(word):
    # tries to change a word into a number, gives None if it is not a number
    word = word.replace(",", "")                     # so 1,200 works
    if word.lower().lstrip("+-") in ("nan", "inf", "infinity"):
        return None                                  # float() accepts these but they are not amounts
    try:
        return float(word)
    except ValueError:
        return None


def parse_entry(line):
    # "KFC lunch 850"  ->  ("KFC lunch", 850.0)
    if line is None or line.strip() == "":
        raise InvalidEntryError("The entry is empty.")

    words = line.split()

    # the amount is the last number in the line, so we search from the end
    amount_position = None
    for i in range(len(words) - 1, -1, -1):
        if to_number(words[i]) is not None:
            amount_position = i
            break

    if amount_position is None:
        raise InvalidEntryError("No amount found. End your entry with a number, e.g. chai 120")

    amount = to_number(words[amount_position])
    if amount < 0:
        raise InvalidEntryError("The amount cannot be negative.")
    if amount == 0:
        raise InvalidEntryError("The amount must be greater than zero.")

    # everything except the amount (and words like rs / pkr) is the description
    description_words = []
    for i, word in enumerate(words):
        if i != amount_position and word.lower() not in ("rs", "rs.", "pkr"):
            description_words.append(word)

    if len(description_words) == 0:
        raise InvalidEntryError("Add a short description, e.g. chai 120")

    return " ".join(description_words), amount
