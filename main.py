from axonaut_api import (
    get_quotations,
    get_invoices,
    get_contracts,
    get_projects,
    get_users,
    get_companies,
)
from transforms import (
    quotations_to_df,
    invoices_to_df,
    contracts_to_df,
    projects_to_df,
    users_to_df,
    companies_to_df,
    build_suivi_commandes,
    build_facturation_a_editer,
)
from excel_export import export_workbook


def main():
    print("Récupération des devis...")
    quotations = get_quotations()

    print("Récupération des factures...")
    invoices = get_invoices()

    print("Récupération des contrats...")
    contracts = get_contracts()

    print("Récupération des projets...")
    projects = get_projects()

    print("Récupération des utilisateurs...")
    users = get_users()

    print("Récupération des sociétés...")
    companies = get_companies()

    df_quotations = quotations_to_df(quotations)
    df_invoices = invoices_to_df(invoices)
    df_contracts = contracts_to_df(contracts)
    df_projects = projects_to_df(projects)
    df_users = users_to_df(users)
    df_companies = companies_to_df(companies)

    df_suivi_commandes = build_suivi_commandes(
        df_contracts, df_projects, df_invoices, df_users, df_companies
    )
    df_facturation = build_facturation_a_editer(
        df_contracts, df_projects, df_invoices, df_users, df_companies
    )

    export_workbook({
        "devis": df_quotations,
        "factures": df_invoices,
        "contrats": df_contracts,
        "projets": df_projects,
        "suivi_commandes": df_suivi_commandes,
        "facturation_a_editer": df_facturation,
    })


if __name__ == "__main__":
    main()