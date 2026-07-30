from utils import strip_code_fences
import os
from prompts import SYSTEM_PROMPT, FINAL_JSON_PROMPT
from dotenv import load_dotenv
from openai import OpenAI
from executor import run_python
from logger import log_interaction

load_dotenv()


class DataAnalystAgent:
    def __init__(self):
        self.state = {}
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )

        self.model = os.getenv("OPENAI_MODEL")
        self.conversations = {}
    
    def get_state(self, chat_id):
        if chat_id not in self.state:
            self.state[chat_id] = {}
        return self.state[chat_id]

    def set_state(self, chat_id, key, value):
        self.get_state(chat_id)[key] = value

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

        return strip_code_fences(response.choices[0].message.content)

    def format_reply(self, chat_id, question, python_output):
        messages = [
            {"role": "system", "content": FINAL_JSON_PROMPT},
            {"role": "user", "content": f"Question:\n{question}\n\nPython output:\n{python_output}"}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        return response.choices[0].message.content    


    def reply(self, chat_id, question):
        state = self.get_state(chat_id)
        code = self.generate_python(
            chat_id,
            f"Previous state:\n{state}\n\nUser request:\n{question}"
        )
        execution = run_python(code)
        self.set_state(chat_id, "last_code", code)
        self.set_state(chat_id, "last_execution", execution)


        if not execution["success"]:
            response = execution["stderr"]
        else:
            response = self.format_reply(
                chat_id,
                question,
                execution["stdout"]
            )

        log_interaction(
            chat_id,
            question,
            response,
            code,
            execution["stdout"],
            execution["stderr"],
        )

        return response
