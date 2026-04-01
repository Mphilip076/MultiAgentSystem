from source_fetchers import fetch_clinicaltrials_study, fetch_biomednews_text


def get_sample_inputs():
    ctgov_text = fetch_clinicaltrials_study("AbbVie immunology")
    biomednews_text = fetch_biomednews_text()

    return [
        {
            "source_name": "ClinicalTrials.gov",
            "source_type": "primary_registry",
            "raw_text": ctgov_text,
        },
        {
            "source_name": "Biomednews",
            "source_type": "secondary_news",
            "raw_text": biomednews_text,
        },
    ]