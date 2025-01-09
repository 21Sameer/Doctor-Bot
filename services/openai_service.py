import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def call_open_ai(messages):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content



