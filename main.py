from src.pdf_parser import extract_text
from src.chunker import split_resume
from src.vector_store import create_vector_store, search_resume
from src.llm import ask_llm

# Read PDF
resume_text = extract_text("resumes/sample_resume.pdf")

# Split into chunks
chunks = split_resume(resume_text)

# Create vector database
vector_store = create_vector_store(chunks)

# Ask a question
query = "What programming languages does the candidate know?"

# Retrieve relevant chunks
results = search_resume(vector_store, query)

print(f"Retrieved {len(results)} documents")

answer = ask_llm(query, results)

print("\nAnswer:\n")
print(answer)