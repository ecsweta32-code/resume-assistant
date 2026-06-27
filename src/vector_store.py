
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def create_vector_store(chunks):
    documents = []

    for chunk in chunks:
        documents.append(Document(page_content=chunk))

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory="chroma_db"
    )

    return vector_store

def search_resume(vector_store, query):
    results = vector_store.similarity_search(
        query,
        k=3
    )

    return results