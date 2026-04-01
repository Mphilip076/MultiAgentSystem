import requests


def fetch_clinicaltrials_study(query: str, max_results: int = 1) -> str:
    """
    Very simple starter fetcher.
    Uses ClinicalTrials.gov study fields endpoint.
    """
    url = "https://clinicaltrials.gov/api/query/study_fields"
    params = {
        "expr": query,
        "fields": ",".join([
            "NCTId",
            "BriefTitle",
            "Condition",
            "InterventionName",
            "Phase",
            "OverallStatus",
            "BriefSummary",
            "PrimaryOutcomeMeasure",
            "PrimaryCompletionDate"
        ]),
        "min_rnk": 1,
        "max_rnk": max_results,
        "fmt": "json"
    }

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    studies = data.get("StudyFieldsResponse", {}).get("StudyFields", [])
    if not studies:
        return "No ClinicalTrials.gov study found."

    s = studies[0]

    def first(field: str) -> str:
        values = s.get(field, [])
        return values[0] if values else "N/A"

    return f"""
NCT ID: {first("NCTId")}
Title: {first("BriefTitle")}
Condition: {first("Condition")}
Intervention: {first("InterventionName")}
Phase: {first("Phase")}
Status: {first("OverallStatus")}
Summary: {first("BriefSummary")}
Primary Outcome: {first("PrimaryOutcomeMeasure")}
Primary Completion Date: {first("PrimaryCompletionDate")}
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