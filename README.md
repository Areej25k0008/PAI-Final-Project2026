# PaisaPal - Console Expense Tracker with Automatic Categorisation

AL-2001 Programming for Artificial Intelligence (Lab), Fall 2026, FAST-NUCES Karachi

Type one line like `KFC lunch 850` or `chai 120`. PaisaPal finds the amount,
predicts the category (Food, Transport, Bills, Shopping, Fun, Education),
saves the entry, and gives monthly summaries, budget warnings, three charts
and totals in other currencies.

**Group:** Areej Hasan (25K-0008) and Wajeeh Hasan (25K-0030), BAI-3A

## How to run

pip install -r requirements.txt
py main.py


## Menu

| Option | What it does |
| 1 | Add an expense from one line of text |
| 2 | Monthly summary with percentages and budget warnings |
| 3 | Set monthly budgets, list months that went over |
| 4 | Three charts (saved in the `charts` folder) |
| 5 | A month's total in USD, EUR and GBP |
| 6 | Compare keyword rules and TF-IDF + Naive Bayes |
| 7 | Five biggest expenses and number of large ones |
| 8 | Switch the classifier that option 1 uses |

## Files

| File | Owner | Content |
| `models.py` | Areej | Entry, Expense, Budget classes and the entry parser |
| `storage.py` | Areej | saving/loading entries (CSV) and budgets (JSON) |
| `currency.py` | Areej | exchange-rate API with saved copy |
| `main.py` | Areej | the menu |
| `classifier.py` | Wajeeh | text cleaning, keyword and Naive Bayes classifiers |
| `analysis.py` | Wajeeh | Pandas/NumPy summaries and the three charts |
| `data/` | both | `expenses_labelled.csv` (training data), `entries.csv` (saved expenses, demo data included), `rates.json` (saved exchange rates) |

## Data sources

* Exchange rates: https://open.er-api.com/v6/latest/USD - **Rates By Exchange Rate API**
  (no key needed, called once per session, last good reply saved in `data/rates.json`).
* `expenses_labelled.csv` was written by the group.
* `entries.csv` has demo entries so the charts work on the first run. Delete
  everything under the first (header) line to start fresh.

## Limitations

* The category prediction is not perfect, option 6 shows the real accuracy.
* Entries cannot be edited or deleted.
* All spending data stays on the computer. Only the exchange-rate request goes online.
