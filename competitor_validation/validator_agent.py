#from crewai import Agent, Task, Crew, Process

from llm_client import validate_with_ollama


class DataValidationRunner:
    def run_validation(self, source_name: str, source_type: str, raw_text: str):
        return validate_with_ollama(source_name, source_type, raw_text)
    


# class DataValidationRunner:
#     def __init__(self):
#         self.auditor = Agent(
#             role="Data Auditor",
#             goal="Validate clinical and competitor intelligence findings conservatively.",
#             backstory=(
#                 "You are a clinical trial data specialist. "
#                 "You treat every claim as guilty until proven innocent. "
#                 "You are strict about source quality, evidence strength, and reporting significance."
#             ),
#             verbose=True,
#             allow_delegation=False
#         )

#     def run_validation(self, source_name: str, source_type: str, raw_text: str):
#         # We use CrewAI as the orchestration shell,
#         # but the actual scoring call is handled by Ollama in Python for reliability.
#         task = Task(
#             description=(
#                 f"Validate one finding from {source_name}. "
#                 f"Source type: {source_type}. "
#                 f"Return structured validation output."
#             ),
#             expected_output="A structured validation result for one source finding.",
#             agent=self.auditor
#         )

#         crew = Crew(
#             agents=[self.auditor],
#             tasks=[task],
#             process=Process.sequential,
#             verbose=True
#         )

#         # Kick off the crew to preserve the architecture pattern
#         crew.kickoff()

#         # Then run the actual validator
#         return validate_with_ollama(source_name, source_type, raw_text)
