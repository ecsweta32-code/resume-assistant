# main.py
import os
from dotenv import load_dotenv
from src.graph import app  # Import your compiled LangGraph workflow

# Load environment variables (API keys, etc.)
load_dotenv()

def run_resume_screener(resume_path: str, job_description: str):
    print("🚀 Starting AI Resume Screening Pipeline...")
    
    # 1. Read the resume PDF text 
    # (Using your Phase 1 PDF parser logic - mock placeholder shown here)
    print("📄 Parsing Resume PDF...")
    resume_text = f"Sample extracted text from {resume_path}. Experience with Python and FastAPI."
    
    # 2. Prepare the initial state inputs required by your graph
    initial_state = {
        "resume_text": resume_text,
        "job_description": job_description,
        "resume_chunks": [],       # Will be populated by extract_and_retrieve_node
        "score_report": {},        # Will be populated by scoring_node
        "summary": "",             # Will be populated by summary_node
        "interview_questions": [], # Will be populated by questions_node
        "final_report": ""         # Will be populated by compile_report_node
    }
    
    # 3. Invoke the LangGraph workflow
    # LangGraph handles the parallel execution of your nodes seamlessly!
    print("🧠 Analyzing profile and running parallel evaluation...")
    final_output = app.invoke(initial_state)
    
    # 4. Print or save the final generated markdown report
    print("\n==================================================")
    print(final_output["final_report"])
    print("==================================================")

if __name__ == "__main__":
    # Test Data
    sample_jd = """
    Python Developer
    Skills Required:
    - Python
    - FastAPI
    - SQL
    - Docker
    - LangGraph
    - AWS
    """
    
    # Run the application
    run_resume_screener(
        resume_path="resumes/sample_resume.pdf", 
        job_description=sample_jd
    )