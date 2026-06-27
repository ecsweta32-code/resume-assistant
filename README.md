# AI Resume Screening Assistant

An AI-powered Resume Screening Assistant built using LangChain, ChromaDB, Hugging Face Embeddings, and Google Gemini.

## Features

- Extract text from PDF resumes
- Split resumes into semantic chunks
- Generate embeddings
- Store embeddings in ChromaDB
- Retrieve relevant resume sections using RAG
- Answer questions using Gemini

## Tech Stack

- Python
- LangChain
- ChromaDB
- Hugging Face Embeddings
- Google Gemini
- pypdf

## Project Structure

```
resume-assistant/
│
├── resumes/
├── src/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Run

```bash
pip install -r requirements.txt
python main.py
```