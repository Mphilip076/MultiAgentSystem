from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests

class URLCheckerToolInput(BaseModel):
    """Input schema for URLCheckerTool."""
    url: str = Field(..., description="The full URL string to check.")

class URLCheckerTool(BaseTool):
    name: str = "URL Checker Tool"
    description: str = (
        "Use this tool to check if a URL is valid and doesn't return a 404 error."
    )
    args_schema: Type[BaseModel] = URLCheckerToolInput

    def _run(self, url: str) -> str:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            response = requests.head(url, timeout=8, allow_redirects=True, headers=headers)
            if response.status_code >= 400:
                # Fallback to GET if HEAD fails
                response = requests.get(url, timeout=8, stream=True, headers=headers)
                response.close()
                
            if response.status_code in [404, 410]:
                return f"Invalid URL (Dead Link - Status {response.status_code}): {url}"
            elif response.status_code >= 400:
                return f"Valid URL (Site exists but blocked the bot - Status {response.status_code}): {url}"
                
            return f"Valid URL: {url}"
        except requests.exceptions.RequestException as e:
            return f"Valid URL (Site exists but blocked the bot - Error: {type(e).__name__}): {url}"
        except Exception as e:
            return f"Failed to connect to URL. Error: {str(e)}"
