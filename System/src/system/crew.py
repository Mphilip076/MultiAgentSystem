from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from pydantic import BaseModel, Field
from typing import List

# Import requested tools
from crewai_tools import SerperDevTool
from crewai.tools import tool

# Initialize the tools
search_tool = SerperDevTool()

@tool("Email Sender Tool")
def send_email_tool(report_content: str) -> str:
    """Use this tool to send the finalized email containing the strategic report to the executive team."""
    # Replace this print statement with actual SMTP/SendGrid/API logic!
    print("--- SIMULATING EMAIL SEND ---")
    print(report_content)
    print("-----------------------------")
    return "Email successfully sent!"

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
            # llm='groq/llama-3.3-70b-versatile'
        )

    @agent
    def data_validator(self) -> Agent:
        return Agent(
            config=self.agents_config['data_validator'], 
            verbose=True
            # llm='groq/llama-3.1-8b-instant' # 6k TPM pool
        )

    @agent
    def report_creator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_creator'], 
            verbose=True
            # llm='groq/gemma2-9b-it' # 15k TPM pool
        )

    @agent
    def report_validator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_validator'], 
            verbose=True
            # llm='groq/llama-3.2-3b-preview' # Separate 7k TPM pool
        )

    @agent
    def send_report(self) -> Agent:
        return Agent(
            config=self.agents_config['send_report'], 
            verbose=True,
            tools=[send_email_tool]
            # llm='groq/llama-3.2-1b-preview' # Separate 7k TPM pool
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
