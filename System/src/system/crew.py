from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from pydantic import BaseModel, Field
from typing import List
from crewai_tools import SerperDevTool
import os
import base64
import datetime
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from crewai.tools import tool

# Initialize the tools
search_tool = SerperDevTool()


# Set the scope to only sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(CUR_DIR, '..', '..', 'credentials.json')
TOKEN_PATH = os.path.join(CUR_DIR, '..', '..', 'token.json')

def get_gmail_service():
    """Handles OAuth2 authentication and returns the Gmail service."""
    creds = None
    # token.json stores the user's access and refresh tokens
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        # This will open a browser window for the first run
        if not os.path.exists(CREDENTIALS_PATH):
            raise FileNotFoundError(f"Credentials file not found at {os.path.abspath(CREDENTIALS_PATH)}. Please ensure it exists in the System/ directory.")
            
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

@tool("Email Sender Tool")
def send_email_tool(report_content: str) -> str:
    """Use this tool to send the finalized strategic report to the executive team 
    via the Gmail API. Input should be the full string content of the report.
    """
    recipient_email = "mateoviteri13579@gmail.com"
    
    try:
        service = get_gmail_service()
        message = EmailMessage()
        
        # Structure the email
        message.set_content(report_content)
        message['To'] = recipient_email
        message['From'] = "me"
        message['Subject'] = f"Strategic Impact Report - {datetime.datetime.now().strftime('%Y-%m-%d')}"

        # Gmail API requires the message to be base64url encoded
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        # Execute the send command
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        
        return f"Email successfully sent to {recipient_email}! Message ID: {send_message['id']}"
    
    except Exception as e:
        return f"Failed to send email. Error: {str(e)}"

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
