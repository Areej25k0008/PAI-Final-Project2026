# currency.py  (written by Areej)
# Gets exchange rates from a web API. If the internet is not working
# it uses the last rates we saved in data/rates.json.

import json
from datetime import datetime

import requests

from storage import RATES_FILE

API_URL = "https://open.er-api.com/v6/latest/USD"       # free, no key needed
CURRENCIES = ["PKR", "USD", "EUR", "GBP"]

# the API asks us to ask only once per session, so we remember the answer
saved_rates = None
saved_message = ""


def fetch_live_rates():
    # asks the API for rates, gives None if anything goes wrong
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code != 200:             # 200 means everything is ok
            return None
        data = response.json()
        if data.get("result") != "success":
            return None
        rates = {}
        for code in CURRENCIES:                     # we keep only the currencies we need
            rates[code] = data["rates"][code]
        return rates
    except requests.exceptions.RequestException:    # no internet, timeout, etc.
        return None
    except (KeyError, ValueError):                  # reply was not what we expected
        return None


def load_saved_rates():
    # reads the rates we saved last time
    try:
        with open(RATES_FILE, encoding="utf-8") as file:
            data = json.load(file)
        return data["rates"], data.get("fetched_at", "unknown time")
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None, None


def get_rates():
    # gives (rates, message). Live rates if possible, otherwise the saved ones.
    global saved_rates, saved_message
    if saved_rates is not None:                     # already done in this session
        return saved_rates, saved_message

    rates = fetch_live_rates()
    if rates is not None:
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(RATES_FILE, "w", encoding="utf-8") as file:
            json.dump({"fetched_at": time_now, "base": "USD", "rates": rates}, file, indent=2)
        message = f"Live rates ({time_now}). Rates By Exchange Rate API"
    else:
        rates, time_saved = load_saved_rates()
        if rates is None:
            return None, "No live or saved exchange rates are available."
        message = f"No internet - using SAVED rates from {time_saved}."

    saved_rates = rates
    saved_message = message
    return rates, message


def convert(amount_pkr, target, rates):
    # the API gives rates for 1 USD, so: rupees -> dollars -> target currency
    return amount_pkr / rates["PKR"] * rates[target]


def totals_in_currencies(amount_pkr, rates):
    # list of (currency, amount) tuples
    result = []
    for code in ["USD", "EUR", "GBP"]:
        result.append((code, convert(amount_pkr, code, rates)))
    return result
