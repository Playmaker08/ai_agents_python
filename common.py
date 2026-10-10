import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(timeout=30, max_retries=2)
model = os.getenv("OPENAI_MODEL", "gpt-4o")
