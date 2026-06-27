import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Create Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)

def ask_llm(query, retrieved_docs):

    context = "\n\n".join(doc.page_content for doc in retrieved_docs)

    prompt = f"""
You are an AI Resume Screening Assistant.

Use ONLY the resume below.

Resume:
{context}

Question:
{query}

Answer:
"""

    response = llm.invoke(prompt)

    return response.content