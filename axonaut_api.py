import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = (os.getenv("AXONAUT_API_KEY") or "").strip()
BASE_URL = (os.getenv("AXONAUT_BASE_URL") or "https://axonaut.com/api/v2").strip()

HEADERS = {
    "userApiKey": API_KEY,
    "Accept": "application/json",
}


def _get(endpoint):
    results = []
    page = 1

    while True:
        headers = HEADERS.copy()
        headers["page"] = str(page)

        url = f"{BASE_URL}/{endpoint}"
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code not in (200, 403):
            response.raise_for_status()

        data = response.json()

        if isinstance(data, list):
            results.extend(data)
            break

        if "results" in data and "pages" in data:
            results.extend(data.get("data", []))

            if page >= data["pages"]:
                break

            page += 1
        else:
            break

    return results

def get_quotations():
    return _get("quotations")


def get_invoices():
    return _get("invoices")


def get_contracts():
    return _get("contracts")


def get_projects():
    return _get("projects")


def get_users():
    return _get("users")


def get_companies():
    return _get("companies")
