# storage.py  (written by Areej)
# Saving and loading files: the entries (CSV) and the budgets (JSON).

import os
import csv
import json
from datetime import date

from models import Expense, Budget

# paths of our files, they are made from the folder where this file is
# so the program works from any place
project_folder = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(project_folder, "data")
ENTRIES_FILE = os.path.join(data_folder, "entries.csv")
BUDGET_FILE = os.path.join(data_folder, "budgets.json")
LABELLED_FILE = os.path.join(data_folder, "expenses_labelled.csv")
RATES_FILE = os.path.join(data_folder, "rates.json")

FIELDS = ["date", "description", "amount", "category"]


# ---------------- entries (CSV) ----------------

def save_entry(expense):
    # adds one expense at the end of entries.csv
    os.makedirs(data_folder, exist_ok=True)
    # the header line is only written when the file is new or empty
    need_header = not os.path.exists(ENTRIES_FILE) or os.path.getsize(ENTRIES_FILE) == 0
    try:
        with open(ENTRIES_FILE, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            if need_header:
                writer.writeheader()
            writer.writerow(expense.to_dict())
        return True
    except PermissionError:
        print("Cannot write to entries.csv. Is it open in another program (like Excel)?")
        return False


def load_entries():
    # reads entries.csv and gives a list of Expense objects
    entries = []
    bad_rows = 0
    try:
        with open(ENTRIES_FILE, newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                try:
                    entry_date = date.fromisoformat(row["date"])
                    entries.append(Expense(entry_date, row["description"],
                                           float(row["amount"]), row["category"] or "Other"))
                except (ValueError, KeyError, TypeError):
                    bad_rows += 1    # a damaged row, we skip it
    except FileNotFoundError:
        return []         # no file yet = no entries yet
    if bad_rows > 0:
        print(f"Note: {bad_rows} damaged row(s) in entries.csv were skipped.")
    return entries


# ---------------- budgets (JSON) ----------------

def save_budget(budget):
    os.makedirs(data_folder, exist_ok=True)
    with open(BUDGET_FILE, "w", encoding="utf-8") as file:
        json.dump(budget.limits(), file, indent=2)


def load_budget():
    budget = Budget()
    try:
        with open(BUDGET_FILE, encoding="utf-8") as file:
            saved = json.load(file)
        for category, limit in saved.items():
            try:
                budget.set_limit(category, float(limit))
            except (ValueError, TypeError):
                pass                        # ignore a bad line in the file
    except FileNotFoundError:
        pass                                # no budgets saved yet
    except (json.JSONDecodeError, AttributeError):
        print("Note: budgets.json is damaged, starting with no budgets.")
    return budget
