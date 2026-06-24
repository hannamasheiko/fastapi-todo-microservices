from pydantic import BaseModel
from openai import OpenAI

from ai_service.app.config import settings


class OpenAIClient:
    """Wrapper around OpenAI Responses API."""

    def __init__(self) -> None:
        self.model = settings.openai_model
        self.api_key = settings.openai_api_key

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(api_key=self.api_key)

    def generate_text(self, prompt: str) -> str:
        """Send a simple text prompt to OpenAI and return a text response."""
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text

    def generate_structured_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ) -> BaseModel:
        """Send prompts to OpenAI and parse response into a Pydantic model."""
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            text_format=response_model,
        )

        return response.output_parsed


openai_client = OpenAIClient()