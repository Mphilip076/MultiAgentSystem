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

class ReportTemplate(BaseModel):
    title: str = Field(default="Untitled", description="The title of the report. Remove 'Research Dossier:' from the title.")
    company: str = Field(default="Unknown", description="The name of the primary company involved (or source name if N/A).")
    date: str = Field(default="Unknown Date", description="The date of the event or report.")
    what_happened: str = Field(default="", description="A clear and concise summary of the core event or news.")
    impact_level: str = Field(default="Medium", description="The assessed level of impact for AbbVie (e.g., 'High', 'Medium', or 'Low').")
    competitive_impact: str = Field(default="", description="Detailed analysis of how this impacts AbbVie from a Competitive Intelligence (CI) Point of View.")
    why_it_matters: str = Field(default="", description="Explanation of the strategic significance and alignment with company goals.")
    tell_me_more: str = Field(default="", description="The actual verified facts and detailed background context extracted from the validated data.")
    outlook: str = Field(default="", description="Actionable strategic recommendations, future outlook, and competitor activities to monitor.")
    source_information: str = Field(default="", description="A numbered list of all sources and exact URLs used.")

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
            config=self.tasks_config['report_creation_task'],
            output_json=ReportTemplate 
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
