import requests

def fetch_clinicaltrials_study(query: str, max_results: int = 1) -> str:
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.term": query,
        "pageSize": max_results,
        "format": "json",
    }

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    studies = data.get("studies", [])
    if not studies:
        return f"No ClinicalTrials.gov study found for query: {query}"

    study = studies[0]

    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    conditions = protocol.get("conditionsModule", {})
    arms = protocol.get("armsInterventionsModule", {})
    description = protocol.get("descriptionModule", {})
    outcomes = protocol.get("outcomesModule", {})

    nct_id = identification.get("nctId", "N/A")
    title = identification.get("briefTitle", "N/A")

    condition_list = conditions.get("conditions", [])
    condition_text = ", ".join(condition_list) if condition_list else "N/A"

    interventions = arms.get("interventions", [])
    intervention_names = [i.get("name", "N/A") for i in interventions if isinstance(i, dict)]
    intervention_text = ", ".join(intervention_names) if intervention_names else "N/A"

    overall_status = status.get("overallStatus", "N/A")
    brief_summary = description.get("briefSummary", "N/A")

    primary_outcomes = outcomes.get("primaryOutcomes", [])
    if primary_outcomes and isinstance(primary_outcomes[0], dict):
        primary_outcome_text = primary_outcomes[0].get("measure", "N/A")
    else:
        primary_outcome_text = "N/A"

    completion_date = status.get("primaryCompletionDateStruct", {}).get("date", "N/A")

    design = protocol.get("designModule", {})
    phases = design.get("phases", [])
    phase_text = ", ".join(phases) if phases else "N/A"

    return f"""
NCT ID: {nct_id}
Title: {title}
Condition: {condition_text}
Intervention: {intervention_text}
Phase: {phase_text}
Status: {overall_status}
Summary: {brief_summary}
Primary Outcome: {primary_outcome_text}
Primary Completion Date: {completion_date}
""".strip()

def fetch_biomednews_text() -> str:
    """
    Placeholder adapter.
    Replace this with the actual Biomednews URL, RSS feed, API, or scraped article text.
    """
    return """
Biomednews sample:
Company X announced positive Phase 2 data in patients with moderate to severe disease Y.
The company stated the trial met its primary endpoint and plans to advance into Phase 3.
No trial identifier or peer-reviewed publication was provided in this summary.
""".strip()