from typing import TypedDict, List

class ScreeningState(TypedDict):
    # Inputs
    resume_text: str
    job_description: str
    resume_chunks: List[str]
    
    # Outputs from parallel nodes
    score_report: dict       # e.g., {"score": 78, "matched": [...], "missing": [...]}
    summary: str             # Bullet points
    interview_questions: List[str]
    
    # Final output
    final_report: str