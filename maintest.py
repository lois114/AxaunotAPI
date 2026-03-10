from axonaut_api import (
    get_quotations,
    get_invoices,
    get_contracts,
    get_projects,
    get_customfields,
    get_users,
    get_opportunities,
    get_companies,
    get_project_natures,
    get_supplier_contracts,
)
import json


def print_first_item(name, data):
    print(f"\n=== {name.upper()} ===")
    print("Type:", type(data))
    print("Count:", len(data) if hasattr(data, "__len__") else "N/A")

    if isinstance(data, list) and data:
        print(f"\n--- Premier élément {name} ---")
        print(json.dumps(data[0], indent=2, ensure_ascii=False))
    elif isinstance(data, dict):
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("Aucune donnée")


def safe_call(name, func):
    try:
        data = func()
        print_first_item(name, data)
        return data
    except Exception as e:
        print(f"\n=== {name.upper()} ===")
        print(f"Erreur: {e}")
        return None


def main():
    safe_call("quotations", get_quotations)
    safe_call("invoices", get_invoices)
    safe_call("contracts", get_contracts)
    safe_call("projects", get_projects)
    safe_call("customfields", get_customfields)
    safe_call("users", get_users)
    safe_call("opportunities", get_opportunities)
    safe_call("companies", get_companies)
    safe_call("project_natures", get_project_natures)
    safe_call("supplier_contracts", get_supplier_contracts)


if __name__ == "__main__":
    main()