from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from pydantic import BaseModel, Field
from crewai_tools import SerperDevTool
from .tools.email_tool import EmailSenderTool
from .tools.url_tool import URLCheckerTool

# Initialize the tools
search_tool = SerperDevTool()
url_check_tool = URLCheckerTool()
send_email_tool = EmailSenderTool()

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
            tools=[search_tool],
            max_iter=3,
            llm=LLM(model="anthropic/claude-haiku-4-5-20251001", temperature=0.2, max_tokens=4096)
        )

    @agent
    def data_validator(self) -> Agent:
        return Agent(
            config=self.agents_config['data_validator'], 
            verbose=True,
            tools=[url_check_tool],
            max_iter=3,
            llm=LLM(model="anthropic/claude-haiku-4-5-20251001", temperature=0.2, max_tokens=4096)
        )

    @agent
    def report_creator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_creator'], 
            verbose=True,
            llm=LLM(model="anthropic/claude-sonnet-4-5-20250929", temperature=0.2, max_tokens=4096)
        )

    @agent
    def report_validator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_validator'], 
            verbose=True,
            llm=LLM(model="anthropic/claude-haiku-4-5-20251001", temperature=0.2, max_tokens=4096)
        )

    @agent
    def send_report(self) -> Agent:
        return Agent(
            config=self.agents_config['send_report'], 
            verbose=True,
            tools=[send_email_tool],
            max_iter=3,
            llm=LLM(model="anthropic/claude-sonnet-4-5-20250929", temperature=0.2, max_tokens=4096)
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
            config=self.tasks_config['report_creation_task']
        )

    @task
    def report_validation_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_validation_task'],
            output_file='final_report.md'
        )

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
