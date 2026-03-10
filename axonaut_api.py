import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AXONAUT_API_KEY")
BASE_URL = os.getenv("AXONAUT_BASE_URL", "https://axonaut.com/api/v2")

HEADERS = {
    "userApiKey": API_KEY,
    "Accept": "application/json",
}


def _get(endpoint: str):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    print(f"{endpoint} status:", response.status_code)
    print(f"{endpoint} response:", response.text[:300])
    response.raise_for_status()
    return response.json()


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