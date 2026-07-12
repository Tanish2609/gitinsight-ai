import os

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    raise ValueError("MISTRAL_API_KEY not found.")

llm = ChatMistralAI(
    model="mistral-medium-3-5",   
    api_key=api_key,
    temperature=0,
)