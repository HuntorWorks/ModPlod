import os
from dotenv import load_dotenv
from rich import print

from openai import OpenAI


def get_token_usage_per_request(gpt_response):
    return gpt_response.usage.completion_tokens, gpt_response.usage.prompt_tokens, gpt_response.usage.total_tokens


class OpenAIManager:

    def __init__(self):
        self.conversation_history = []
        self.prompt_token_total = 0
        self.completions_token_total = 0
        self.all_tokens_total = 0
        try:
            load_dotenv()
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except NotImplementedError:
            print(f"[bold red]ERROR[/bold red]: You forgot to set an .env environment, or didn't set an OPENAI_API_KEY in .env")

    def respond_without_chat_history(self, message, gpt_model, temperature, max_tokens, system_message=None, send_system_message=False):
        self.prompt_token_total = 0
        self.completions_token_total = 0
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

        tokens = get_token_usage_per_request(response)
        self.completions_token_total = tokens[0]
        self.prompt_token_total = tokens[1]
        self.add_tokens_to_history(tokens[2])

        response_text = response.choices[0].message.content.strip()

        return response_text

    def respond_with_chat_history(self, message, gpt_model, temperature, max_tokens, system_message=None, send_system_message=False):
        self.prompt_token_total = 0
        self.completions_token_total = 0
        response = None
        if system_message is None:
            system_message = {""}

        if not message:
            print("[bold red]ERROR[/bold red]:  Didn't receive prompt.  Discontinuing process.")
            return

        if send_system_message:
            response = self.client.chat.completions.create(
                model=gpt_model,
                messages=self.conversation_history,
                temperature=temperature,
                max_completion_tokens=max_tokens
            )
        else:
            response = self.client.chat.completions.create(
                model=gpt_model,
                messages=self.conversation_history,
                temperature=temperature,
                max_completion_tokens=max_tokens
            )

        tokens = get_token_usage_per_request(response)
        self.completions_token_total = tokens[0]
        self.prompt_token_total = tokens[1]
        self.add_tokens_to_history(tokens[2])

        response_text = response.choices[0].message.content.strip()
        self.add_to_history({"role": "assistant", "content": response_text})

        return response_text

    def add_to_history(self, text_to_add):
        self.conversation_history.append(text_to_add)

    def add_tokens_to_history(self, tokens):
        self.all_tokens_total += tokens
