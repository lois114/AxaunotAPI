import pandas as pd

def normalize_id(series):
    return (
        pd.to_numeric(series, errors="coerce")
        .astype("Int64")
        .astype(str)
        .replace("<NA>", "")
    )

def quotations_to_df(quotations):
    rows = []
    for q in quotations:
        rows.append({
            "id": q.get("id"),
            "numero": q.get("number"),
            "titre": q.get("title"),
            "date": q.get("date"),
            "expiration": q.get("expiry_date"),
            "statut": q.get("status"),
            "client": q.get("company_name"),
            "user_id": q.get("user_id"),
            "project_id": q.get("project_id"),
            "opportunity_id": q.get("opportunity_id"),
            "contract_id": q.get("contract_id"),
            "montant_ht": q.get("pre_tax_amount"),
            "montant_ttc": q.get("total_amount"),
        })
    return pd.DataFrame(rows)


def invoices_to_df(invoices):
    rows = []
    for inv in invoices:
        company = inv.get("company") or {}
        rows.append({
            "id": inv.get("id"),
            "numero": inv.get("number"),
            "numero_commande": inv.get("order_number"),
            "date": inv.get("date"),
            "echeance": inv.get("due_date"),
            "date_paiement": inv.get("paid_date"),
            "client": company.get("name"),
            "company_id": company.get("id"),
            "commercial_facture": inv.get("business_user"),
            "project_id": inv.get("project_id"),
            "contract_id": inv.get("contract_id"),
            "montant_ht": inv.get("pre_tax_amount"),
            "montant_ttc": inv.get("total"),
            "restant_du": inv.get("outstanding_amount"),
        })
    return pd.DataFrame(rows)


def contracts_to_df(contracts):
    rows = []

    for c in contracts:
        departement = "Non défini"
        sous_traitance = 0

        custom_fields = c.get("custom_fields") or []

        if isinstance(custom_fields, dict):
            departement = custom_fields.get("Département") or "Non défini"
            sous_traitance = custom_fields.get("Sous-Traitance") or 0

        elif isinstance(custom_fields, list):
            for field in custom_fields:
                if isinstance(field, dict):
                    if field.get("name") == "Département":
                        departement = field.get("value") or "Non défini"
                    elif field.get("name") == "Sous-Traitance":
                        sous_traitance = field.get("value") or 0

        company = c.get("company") or {}
        project = c.get("project") or {}
        quotation = c.get("quotation") or {}

        project_number = project.get("number")
        project_name = project.get("name")

        if project_name:
            commande = project_name.replace("_", " ")
        elif project_number:
            commande = project_number
        elif c.get("name"):
            commande = c.get("name")
        else:
            commande = str(c.get("id"))


        rows.append({
            "contract_id": c.get("id"),
            "commande": commande,
            "commande_source": c.get("name"),
            "date_debut": c.get("start_date"),
            "date_fin": c.get("end_date"),
            "user_id": c.get("user_id"),
            "client": company.get("name"),
            "company_id": company.get("id"),
            "project_id": project.get("id"),
            "project_number": project_number,
            "project_name": project_name,
            "departement": departement,
            "sous_traitance": sous_traitance,
            "montant_devis_ht": quotation.get("pre_tax_amount"),
            "premiere_facture_prevue": c.get("first_invoice_planned_date"),
            "facturation_recurrente": c.get("generate_and_send_recurring_invoices"),
            "frequence_facturation_mois": c.get("invoice_frequency_in_months"),
            "invoices_id": c.get("invoices_id") or [],
        })

    return pd.DataFrame(rows)



def projects_to_df(projects):
    rows = []
    for p in projects:
        workforces = p.get("workforces") or []
        premier_commercial = workforces[0]["fullname"] if workforces else None

        rows.append({
            "project_id": p.get("id"),
            "project_name": p.get("name"),
            "project_number": p.get("number"),
            "actual_start": p.get("actual_start"),
            "actual_end": p.get("actual_end"),
            "estimated_start": p.get("estimated_start"),
            "estimated_end": p.get("estimated_end"),
            "commercial_projet": premier_commercial,
        })
    return pd.DataFrame(rows)


def users_to_df(users):
    rows = []
    for u in users:
        rows.append({
            "user_id": u.get("id"),
            "commercial_nom": u.get("full_name"),
        })
    return pd.DataFrame(rows)


def companies_to_df(companies):
    rows = []
    for c in companies:

        business_manager = c.get("business_manager") or {}
        
        rows.append({
            "company_id": c.get("id"),
            "client": c.get("name"),
            "commercial_company": business_manager.get("name"),
        })
    return pd.DataFrame(rows)


def _prepare_common(df_contracts, df_projects, df_invoices, df_users, df_companies):
    contracts = df_contracts.copy()
    projects = df_projects.copy()
    invoices = df_invoices.copy()
    users = df_users.copy()
    companies = df_companies.copy()

    # types homogènes
    contracts["contract_id"] = normalize_id(contracts["contract_id"])
    contracts["project_id"] = normalize_id(contracts["project_id"])
    contracts["company_id"] = pd.to_numeric(contracts["company_id"], errors="coerce")

    projects["project_id"] = normalize_id(projects["project_id"])

    invoices["contract_id"] = normalize_id(invoices["contract_id"])
    invoices["company_id"] = pd.to_numeric(invoices["company_id"], errors="coerce")
    invoices["montant_ht"] = pd.to_numeric(invoices["montant_ht"], errors="coerce").fillna(0)

    users["user_id"] = pd.to_numeric(users["user_id"], errors="coerce")
    companies["company_id"] = pd.to_numeric(companies["company_id"], errors="coerce")
 

    

    invoices_agg = (
    invoices.groupby("contract_id", as_index=False)
    .agg(
        montant_facture_ht=("montant_ht", "sum"),
        derniere_facture=("date", "max"),
        commercial_facture=("commercial_facture", "first"),
        montant_recurrent_mensuel=("montant_ht", "first"),
    )
    )

    merged = (
    contracts
    .merge(projects, on="project_id", how="left")
    .merge(users, on="user_id", how="left")
    .merge(companies[["company_id", "commercial_company"]], on="company_id", how="left")
    .merge(invoices_agg, on="contract_id", how="left")
    )

    merged["debut"] = merged["date_debut"].fillna(merged["actual_start"]).fillna(merged["estimated_start"])
    merged["fin"] = merged["date_fin"].fillna(merged["actual_end"]).fillna(merged["estimated_end"])

    merged["montant_devis_ht"] = pd.to_numeric(merged["montant_devis_ht"], errors="coerce").fillna(0)
    merged["montant_facture_ht"] = pd.to_numeric(merged["montant_facture_ht"], errors="coerce").fillna(0)
    merged["reste_a_facturer"] = merged["montant_devis_ht"] - merged["montant_facture_ht"]

    merged["commercial"] = (
        merged["commercial_facture"]
        .fillna(merged["commercial_nom"])
        .fillna(merged["commercial_projet"])
        .fillna(merged["commercial_company"])
    )

    merged["fact_prev"] = merged.apply(
        lambda r: "Oui" if r["reste_a_facturer"] > 0 or pd.notna(r["premiere_facture_prevue"]) else "Non",
        axis=1
    )

    merged["montant_recurrent_mensuel"] = merged.apply(
    lambda r: r["montant_recurrent_mensuel"]
    if pd.notna(r["frequence_facturation_mois"]) and r["frequence_facturation_mois"] == 1
    else 0,
    axis=1
    )


    for col in ["debut", "fin", "premiere_facture_prevue", "derniere_facture"]:
        merged[col] = pd.to_datetime(merged[col], errors="coerce")




    merged["prochaine_facture"] = merged["premiere_facture_prevue"].fillna("")
    merged["departement"] = merged["departement"].fillna("")
    merged["sous_traitance"] = (
    merged["sous_traitance"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    )

    merged["sous_traitance"] = pd.to_numeric(
    merged["sous_traitance"],
    errors="coerce"
    ).fillna(0)


    return merged


def build_suivi_commandes(df_contracts, df_projects, df_invoices, df_users, df_companies):
    merged = _prepare_common(df_contracts, df_projects, df_invoices, df_users, df_companies)

    result = merged[[
        "commande",
        "client",
        "debut",
        "fin",
        "fact_prev",
        "commercial",
        "montant_devis_ht",
        "montant_facture_ht",
        "montant_recurrent_mensuel",
        "departement",
        "sous_traitance",
    ]].copy()

    # debug = merged[merged["contract_id"] == "7431712"][
    # ["contract_id", "commande", "montant_devis_ht", "montant_facture_ht"]
    # ]
    # print(debug)

    result.columns = [
        "Commande",
        "Client",
        "Début",
        "Fin",
        "Fact. prév.",
        "Commercial",
        "Montant devis HT",
        "Montant HT",
        "Montant récurrent mensuel",
        "Département",
        "Sous-Traitance",
    ]

    return result.sort_values(by=["Client", "Commande"], na_position="last")


def build_facturation_a_editer(df_contracts, df_projects, df_invoices, df_users, df_companies):
    merged = _prepare_common(df_contracts, df_projects, df_invoices, df_users, df_companies)

    result = merged[[
        "commercial",
        "client",
        "commande",
        "debut",
        "fin",
        "montant_facture_ht",
        "derniere_facture",
        "fact_prev",
        "prochaine_facture",
    ]].copy()

    result.columns = [
        "Commercial",
        "Client",
        "Commande",
        "Date de début",
        "Date de fin",
        "HT",
        "Dernière facture",
        "Fact. prév",
        "Prochaine facture",
    ]

    return result.sort_values(by=["Client", "Commande"], na_position="last")
