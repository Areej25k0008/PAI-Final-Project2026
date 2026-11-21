# analysis.py  (written by Wajeeh)
# Summaries with Pandas and NumPy, and the three charts (Matplotlib + Seaborn).

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from models import CATEGORIES
from storage import ENTRIES_FILE, project_folder

CHARTS_FOLDER = os.path.join(project_folder, "charts")


# ------------------------------------------------------------
# Part 1: Pandas - load, clean and summarise
# ------------------------------------------------------------

def load_dataframe():
    # loads entries.csv into a DataFrame and cleans it
    try:
        df = pd.read_csv(ENTRIES_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=["date", "description", "amount", "category", "month"])

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")    # bad amounts become NaN
    df["date"] = pd.to_datetime(df["date"], errors="coerce")       # bad dates become NaT
    df = df.dropna(subset=["amount", "date"])                      # remove those rows
    df = df[df["amount"] > 0]
    df["category"] = df["category"].fillna("Other")                # missing category
    df["month"] = df["date"].dt.strftime("%Y-%m")                  # like 2026-10
    return df.reset_index(drop=True)


def monthly_summary(df, month):
    # total spending of each category in one month (biggest first)
    this_month = df[df["month"] == month]
    return this_month.groupby("category")["amount"].sum().sort_values(ascending=False)


def summary_pairs(summary):
    # changes the summary into a list of (category, amount) tuples
    pairs = list(zip(summary.index, summary.values))
    return sorted(pairs, key=lambda pair: pair[1], reverse=True)


# ------------------------------------------------------------
# Part 2: NumPy - the months x categories table
# ------------------------------------------------------------

def spending_matrix(df):
    # rows = months, columns = categories, values = total spent
    table = df.pivot_table(index="month", columns="category", values="amount",
                           aggfunc="sum", fill_value=0)
    table = table.reindex(columns=CATEGORIES, fill_value=0)     # same column order always
    return list(table.index), list(table.columns), table.to_numpy(dtype=float)


def category_shares(matrix):
    # percentage of each category in its month, with broadcasting (no loops)
    totals = matrix.sum(axis=1, keepdims=True)      # total of every month
    totals[totals == 0] = 1                         # boolean mask, so we never divide by 0
    return matrix / totals * 100


def month_shares(df, month):
    # gives {"Food": 40.5, ...} for one month
    months, categories, matrix = spending_matrix(df)
    shares = category_shares(matrix)
    row = months.index(month)
    return dict(zip(categories, shares[row]))


def over_budget_report(df, budget):
    # finds every month and category that went over its budget
    months, categories, matrix = spending_matrix(df)
    if len(months) == 0:
        return []
    limits = budget.limits()
    # one limit for every column, np.inf means "no limit set"
    limit_row = np.array([limits.get(c, np.inf) for c in categories])
    too_much = matrix > limit_row               # broadcasting: compares every month with the limits
    rows, cols = np.nonzero(too_much)           # positions where it is True
    report = []
    for r, c in zip(rows, cols):
        report.append((months[r], categories[c], matrix[r, c], limits[categories[c]]))
    return report


# ------------------------------------------------------------
# Part 3: functions with lambda, filter (on Expense objects)
# ------------------------------------------------------------

def top_expenses(entries, n=5):
    # the n biggest expenses
    return sorted(entries, key=lambda e: e.get_amount(), reverse=True)[:n]


def large_expenses(entries, limit=1000):
    # all expenses of limit rupees or more
    return list(filter(lambda e: e.is_large(limit), entries))


# ------------------------------------------------------------
# Part 4: charts
# ------------------------------------------------------------

def save_chart(figure, filename, show):
    os.makedirs(CHARTS_FOLDER, exist_ok=True)
    path = os.path.join(CHARTS_FOLDER, filename)
    figure.tight_layout()
    figure.savefig(path, dpi=120)
    if show:
        plt.show()
    plt.close(figure)
    return path


def category_share_chart(df, show):
    # chart 1: bar chart, share of every category in the total spending
    totals = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    shares = (totals / totals.sum() * 100).reset_index()
    shares.columns = ["category", "percent"]

    figure, axis = plt.subplots(figsize=(8, 5))
    sns.barplot(data=shares, x="category", y="percent", color="steelblue", ax=axis)
    axis.set_title("Share of each category in total spending")
    axis.set_xlabel("Category")
    axis.set_ylabel("Share of spending (%)")
    return save_chart(figure, "category_share.png", show)


def monthly_totals_chart(df, show):
    # chart 2: bar chart, total spending of every month
    monthly = df.groupby("month")["amount"].sum().reset_index()

    figure, axis = plt.subplots(figsize=(8, 5))
    sns.barplot(data=monthly, x="month", y="amount", color="seagreen", ax=axis)
    axis.set_title("Total spending per month")
    axis.set_xlabel("Month")
    axis.set_ylabel("Amount (Rs)")
    return save_chart(figure, "monthly_totals.png", show)


def spending_over_time_chart(df, show):
    # chart 3: line chart, how much was spent on each day
    daily = df.groupby("date")["amount"].sum().reset_index()

    figure, axis = plt.subplots(figsize=(9, 5))
    sns.lineplot(data=daily, x="date", y="amount", marker="o", ax=axis)
    axis.set_title("Daily spending over time")
    axis.set_xlabel("Date")
    axis.set_ylabel("Amount (Rs)")
    axis.tick_params(axis="x", rotation=45)
    return save_chart(figure, "spending_over_time.png", show)


def make_all_charts(df, show=True):
    return [category_share_chart(df, show),
            monthly_totals_chart(df, show),
            spending_over_time_chart(df, show)]
