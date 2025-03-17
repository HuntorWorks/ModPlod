import os
from dotenv import load_dotenv
from rich import print
from openai import OpenAI


class OpenAIManager:

    MAX_REQUEST_TOKENS = 8000

    def __init__(self):
        try:
            load_dotenv()
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except NotImplementedError:
            print(f"[bold red]ERROR[/bold red]: You forgot to set an .env environment, or didn't set an OPENAI_API_KEY in .env")

    def respond_without_chat_history(self, message, gpt_model, temperature, max_tokens, system_message=None, send_system_message=False):
        response = None
        if system_message is None:
            system_message = {""}

        if not message:
            print("[bold red]ERROR[/bold red]:  Didn't receive prompt.  Discontinuing process.")
            return

        if send_system_message:
            response = self.client.chat.completions.create(
                model=gpt_model,
                messages=[
                    system_message,
                    {"role": "user", "content": message}
                ],
                temperature=temperature,
                max_completion_tokens=max_tokens
            )
        else:
            response = self.client.chat.completions.create(
                model=gpt_model,
                messages=[
                    {"role": "user", "content": "message"}
                ],
                temperature=temperature,
                max_completion_tokens=max_tokens
            )

        response_text = response.choices[0].message.content.strip()

        return response_text

    def respond_with_chat_history(self, message, gpt_model, temperature, max_tokens, conversation_history, system_message=None, send_system_message=False):
        response = None
        if system_message is None:
            system_message = {""}

        if not message:
            print("[bold red]ERROR[/bold red]:  Didn't receive prompt.  Discontinuing process.")
            return

        if send_system_message:
            response = self.client.chat.completions.create(
                model=gpt_model,
                messages=conversation_history,
                temperature=temperature,
                max_completion_tokens=max_tokens
            )
        else:
            response = self.client.chat.completions.create(
                model=gpt_model,
                messages=conversation_history,
                temperature=temperature,
                max_completion_tokens=max_tokens
            )

        response_text = response.choices[0].message.content.strip()

        return response_text

