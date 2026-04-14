#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from system.crew import System

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    # Example mocked data from your scraper
    scraped_news_queue = [
        {
            "title": "OpenAI announces new Strawberry AI reasoning models", 
            "link": "https://www.theverge.com/2024/9/12/24242439/openai-o1-model-reasoning-strawberry-chatgpt", 
            "date": "2024-09-12",
            "snippet": "OpenAI is releasing a new series of AI models designed to spend more time thinking before they respond. It's the first in a series of reasoning models focused on complex problem-solving."
        }
    ]

    for article in scraped_news_queue:
        print(f"\n--- Initiating Crew Analysis for: {article['title']} ---\n")
        
        inputs = {
            'topic': 'Competitor AI Development',
            'news_item': article,
            'template': "Hello Team,\n\nPlease find the latest strategic analysis below:\n{report_content}\n\nBest,\nAutomated System",
            'company_goals': "We are aggressively expanding our AI product suite this quarter. Focus on how competitor moves threaten or validate our roadmap."
        }

        try:
            System().crew().kickoff(inputs=inputs)
        except Exception as e:
            raise Exception(f"An error occurred while running the crew on {article['title']}: {e}")
def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        System().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        System().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        System().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = System().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
