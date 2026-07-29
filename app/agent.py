import os

from dotenv import load_dotenv
from openai import OpenAI

from prompts import SYSTEM_PROMPT
from executor import run_python

load_dotenv()


class DataAnalystAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )

        self.model = os.getenv("OPENAI_MODEL")
        self.conversations = {}

    def get_messages(self, chat_id):
        if chat_id not in self.conversations:
            self.conversations[chat_id] = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                }
            ]

        return self.conversations[chat_id]


    def add_user_message(self, chat_id, text):
        self.get_messages(chat_id).append(
            {
                "role": "user",
                "content": text,
            }
        )


    def add_assistant_message(self, chat_id, text):
        self.get_messages(chat_id).append(
            {
                "role": "assistant",
                "content": text,
            }
        )

    def generate_python(self, chat_id, question):
        self.add_user_message(chat_id, question)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.get_messages(chat_id),
        )

        code = response.choices[0].message.content.strip()

        self.add_assistant_message(chat_id, code)

        return code

    def reply(self, chat_id, question):
        code = self.generate_python(chat_id, question)
        execution = run_python(code)

        if not execution["success"]:
            return execution["stderr"]

        return str(execution["stdout"])
