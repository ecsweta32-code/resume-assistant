# Backend

The LangGraph pipeline, RAG nodes, vector store, and all 
backend logic is located in `/src/`.

Key files:
- `src/graph.py` — LangGraph pipeline definition
- `src/nodes.py` — Scoring, summary, interview question nodes
- `src/vector_store.py` — ChromaDB setup
- `src/pdf_parser.py` — Resume PDF extraction
- `src/report_builder.py` — PDF report generation