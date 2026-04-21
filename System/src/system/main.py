#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from system.crew import System

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
warnings.filterwarnings("ignore", category=UserWarning)

def run():
    """
    Run the crew with optimized inputs.
    """
    scraped_news_queue = [
        {
            "title": "Pfizer Secures FDA Approval for Oral GLP-1 and Metsera Acquisition", 
            "link": "https://www.pharmavoice.com/news/pfizer-ceo-strategy", 
            "date": "2026-04-14",
            "snippet": "Pfizer has finalized its acquisition of Metsera and received approval for its once-daily obesity pill."
        }
    ]

    for article in scraped_news_queue:
        print(f"\n--- Initiating Crew Analysis for: {article['title']} ---\n")
        
        # Flattening the article data helps prevent the LLM from getting 
        # confused by raw JSON/Dictionary syntax in the prompt.
        inputs = {
            'topic': 'Biopharmaceutical Market Dynamics and Competitor Strategy',
            'news_item': f"Source: {article['title']}. Content: {article['snippet']}. URL: {article['link']}",
            'template': (
                "TITLE: [title]\n"
                "COMPANY: [company name]\n"
                f"DATE: {datetime.now().strftime('%B %d, %Y')}\n\n"
                "QUICK SUMMARY:\n"
                "[A brief summary of the most important findings]\n\n"
                "KEY TAKEAWAYS:\n"
                "- [bullet point 1]\n"
                "- [bullet point 2]\n"
                "- [bullet point 3]\n"
            ),
            'company_goals': (
                "1. Protect market share in core Immunology and Oncology portfolios. "
                "2. Monitor competitor R&D breakthroughs that may disrupt current standards of care. "
                "3. Identify M&A activity or strategic pivots that shift the industry's capital flow. "
                "4. Assess risks to patent estates and regulatory exclusivity."
            )
        }

        try:
            System().crew().kickoff(inputs=inputs)
        except Exception as e:
            print(f"FAILED: {article['title']}\nError: {e}")