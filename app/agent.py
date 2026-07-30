import json
from formatter import format_reply
import base64
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

        print("=" * 80)
        print(question)
        print("=" * 80)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
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

    def reply(self, chat_id, question, image_path=None, audio_path=None):
        state = self.get_state(chat_id)
        if image_path:
            return self.describe_image(question, image_path)
        code = self.generate_python(
            chat_id,
            f"Previous state:\n{state}\n\nUser request:\n{question}"
        )
        print("=" * 80)
        print(code)
        print("=" * 80)
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

        answer = json.loads(response)["answer"]
        return format_reply(answer)


    def describe_image(self, question, image_path):
        with open(image_path, "rb") as f:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
                                },
                            },
                        ],
                    }
                ],
            )

        return response.choices[0].message.content
