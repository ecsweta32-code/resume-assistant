# src/nodes.py
import os
import sys  # 💡 Added this import

# 💡 Move this to the VERY TOP so Python can find 'src' immediately
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.state import ScreeningState  # Now this will import perfectly!

# Load environment variables from .env file
load_dotenv()

# Initialize the modern Gemini Client (Cleaned up the duplicate client call)
client = genai.Client()
MODEL_NAME = "gemini-2.5-flash"

def extract_and_retrieve_node(state: ScreeningState) -> dict:
    """
    Step 1: Uses the Job Description to search ChromaDB and find the 
    most relevant background chunks from the applicant's resume.
    """
    jd = state["job_description"]
    
    # --- PLUG IN YOUR PHASE 1 CHROMADB LOGIC HERE ---
    # Example mock retrieval representing your semantic search query:
    # results = chroma_collection.query(query_texts=[jd], n_results=5)
    retrieved_chunks = ["Experience with Python, FastAPI backend architectures", "Built vector DB pipelines"] 
    
    return {"resume_chunks": retrieved_chunks}


def scoring_node(state: ScreeningState) -> dict:
    """
    Step 2 (Parallel): Uses Gemini's Structured Output feature to force 
    a reliable JSON response matching a strict schema.
    """
    context = "\n".join(state["resume_chunks"])
    jd = state["job_description"]
    
    prompt = f"""
    You are an expert ATS scanner. Compare the candidate's resume text against the Job Description.
    Provide a score out of 100, list matched technical skills, and list missing required skills.
    
    Job Description: {jd}
    Resume Context: {context}
    """
    
    # Define a Pydantic-style schema inline using Gemini's Type system
    schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "score": types.Schema(type=types.Type.INTEGER, description="A matching score from 0 to 100"),
            "matched_skills": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
            "missing_skills": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
        },
        required=["score", "matched_skills", "missing_skills"],
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.1 # Low temperature for factual parsing
        ),
    )
    
    # Parse the guaranteed valid JSON string into a Python dict
    score_data = json.loads(response.text)
    return {"score_report": score_data}


def summary_node(state: ScreeningState) -> dict:
    """
    Step 3 (Parallel): Generates a high-level summary paragraph and structural bullet points.
    """
    context = "\n".join(state["resume_chunks"])
    jd = state["job_description"]
    
    prompt = f"""
    Review the applicant's background relative to this job opening.
    Provide a concise candidate summary containing a 2-sentence overview followed by 3-4 professional bullet points outlining strengths and gaps.
    
    Job Description: {jd}
    Resume Context: {context}
    """
    
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return {"summary": response.text}


def questions_node(state: ScreeningState) -> dict:
    """
    Step 4 (Parallel): Generates 5 tailored behavioral and architectural interview questions.
    """
    context = "\n".join(state["resume_chunks"])
    jd = state["job_description"]
    
    prompt = f"""
    Based on the gaps and tech stack match between this resume and the target role, 
    generate exactly 5 deeply targeted technical interview questions to evaluate the candidate.
    
    Job Description: {jd}
    Resume Context: {context}
    """
    
    # Force Gemini to return a clean JSON array of strings
    schema = types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING))
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema),
    )
    
    questions_list = json.loads(response.text)
    return {"interview_questions": questions_list}


def compile_report_node(state: ScreeningState) -> dict:
    """
    Step 5 (Fan-In / Merge): Joins all parallel data points together into a beautiful Markdown report.
    """
    score_report = state["score_report"]
    summary = state["summary"]
    questions = "\n".join([f"{i+1}. {q}" for i, q in enumerate(state["interview_questions"])])
    
    matched = ", ".join(score_report['matched_skills'])
    missing = ", ".join(score_report['missing_skills'])
    
    markdown_report = f"""
# CANDIDATE SCREENING REPORT

## Overall Match Score: {score_report['score']}/100

### Skill Breakdown
* **Matched Skills:** {matched if matched else 'None identified'}
* **Missing Skills:** {missing if missing else 'None identified'}

---

### Candidate Summary
{summary}

---

### Recommended Interview Questions
{questions}
"""
    return {"final_report": markdown_report}