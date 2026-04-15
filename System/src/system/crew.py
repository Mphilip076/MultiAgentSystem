from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from pydantic import BaseModel, Field
from typing import List

# Import requested tools
from crewai_tools import SerperDevTool
from crewai.tools import tool
import os
import datetime

# Initialize the tools
search_tool = SerperDevTool()

@tool("Email Sender Tool")
def send_email_tool(report_content: str) -> str:
    """Use this tool to simulate sending the finalized strategic report to the executive team.
    It will print the email structure to the console for review.
    """
    recipient_email = "abbvie@uic.edu"
    
    print("\n" + "="*60)
    print("From:      Team404" )
    print(f"To:      {recipient_email}")
    print(f"Subject: Strategic Impact Report {datetime.datetime.now()}")
    print("-" * 60)
    print(report_content)
    print("="*60 + "\n")

    return f"Email successfully sent to {recipient_email}!"

class ReportTemplate(BaseModel):
    executive_summary: str = Field(description="A high-level summary of the news and its immediate strategic implications.")
    historical_context: str = Field(description="Background information leading up to this event.")
    verified_facts: List[str] = Field(description="A bulleted list of strictly verified facts extracted from the validated data.")
    competitive_impact: str = Field(description="Detailed analysis on how this impacts the competitive landscape.")
    recommended_actions: List[str] = Field(description="Actionable strategic recommendations based on the findings.")

@CrewBase
class System():
    """System crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # --- AGENTS --- #
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], 
            verbose=True,
            tools=[search_tool]
        )

    @agent
    def data_validator(self) -> Agent:
        return Agent(
            config=self.agents_config['data_validator'], 
            verbose=True
        )

    @agent
    def report_creator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_creator'], 
            verbose=True
        )

    @agent
    def report_validator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_validator'], 
            verbose=True
        )

    @agent
    def send_report(self) -> Agent:
        return Agent(
            config=self.agents_config['send_report'], 
            verbose=True,
            tools=[send_email_tool]
        )

    # --- TASKS --- #
    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config['research_task'])

    @task
    def data_validation_task(self) -> Task:
        return Task(config=self.tasks_config['data_validation_task'])

    @task
    def report_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_creation_task'],
            output_pydantic=ReportTemplate 
        )

    @task
    def report_validation_task(self) -> Task:
        return Task(config=self.tasks_config['report_validation_task'])

    @task
    def send_report_task(self) -> Task:
        return Task(config=self.tasks_config['send_report_task'])

    @crew
    def crew(self) -> Crew:
        """Creates the System crew"""
        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            verbose=True,
            process=Process.sequential
        )
