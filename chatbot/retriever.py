import os
import json
import pandas as pd
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb

# ENV LOADING
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "AI Solutions"

# Paths
JSON_PATH = "data_ai/ai_solution_dataset.json"
CHROMA_PATH = "data1/ai"

# ------------------------
# Load JSON Knowledge Base with Structured Processing
# ------------------------
def load_json_kb(json_path):
    if not os.path.exists(json_path):
        print(f"⚠️ No JSON file found at {json_path}")
        return []

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    kb_docs = []

    # Handle company as one structured doc
    company = data.get("company", {})
    about = company.get("about", {})
    company_content = (
        f"Company: {company.get('name', '')}\n"
        f"Story: {about.get('story', '')}\n"
        f"Founded: {about.get('founded', '')}\n"
        f"Team Size: {about.get('team_size', '')}\n"
        f"Clients: {about.get('clients', '')}\n"
        f"Countries: {about.get('countries', '')}\n"
        f"Mission: {company.get('mission', '')}\n"
        f"Vision: {company.get('vision', '')}\n"
        f"Values: {', '.join(company.get('values', []))}\n"
        f"Trusted By: {', '.join(company.get('trusted_by', []))}\n"
        f"CTA: {company.get('cta', '')}"
    )
    if len(company_content) > 100:
        kb_docs.append(Document(
            page_content=company_content, 
            metadata={"source": "json_kb", "section": "company", "category": "overview"}
        ))

    # Handle solutions as per-item docs
    solutions = data.get("solutions", [])
    for i, sol in enumerate(solutions):
        sol_content = (
            f"Solution {i+1}: {sol.get('name', '')}\n"
            f"Category: {sol.get('category', '')}\n"
            f"Overview: {sol.get('overview', '')}\n"
            f"Features: {', '.join(sol.get('features', []))}\n"
            f"Benefits: {', '.join(sol.get('benefits', []))}\n"
            f"Use Cases: {', '.join(sol.get('use_cases', []))}"
        )
        if len(sol_content) > 100:
            kb_docs.append(Document(
                page_content=sol_content, 
                metadata={"source": "json_kb", "section": "solutions", "category": sol.get('category', '')}
            ))

    # Handle events as per-item docs
    events = data.get("events", [])
    for i, event in enumerate(events):
        event_content = (
            f"Event {i+1}: {event.get('name', '')}\n"
            f"Type: {event.get('type', '')}\n"
            f"Date: {event.get('date', '')}\n"
            f"Location: {event.get('location', '')}\n"
            f"Highlights: {', '.join(event.get('highlights', []))}\n"
            f"Our Participation: {', '.join(event.get('our_participation', []))}\n"
            f"Key Takeaways: {', '.join(event.get('key_takeaways', []))}"
        )
        if len(event_content) > 100:
            kb_docs.append(Document(
                page_content=event_content, 
                metadata={"source": "json_kb", "section": "events", "category": event.get('type', '')}
            ))

    # Handle projects as per-item docs
    projects = data.get("projects", [])
    for i, proj in enumerate(projects):
        proj_content = (
            f"Project {i+1}: {proj.get('name', '')}\n"
            f"Date: {proj.get('date', '')}\n"
            f"Overview: {proj.get('overview', '')}"
        )
        if len(proj_content) > 100:
            kb_docs.append(Document(
                page_content=proj_content, 
                metadata={"source": "json_kb", "section": "projects", "category": "project"}
            ))

    # Handle articles as per-item docs
    articles = data.get("articles", [])
    for i, art in enumerate(articles):
        art_content = (
            f"Article {i+1}: {art.get('title', '')}\n"
            f"Date: {art.get('date', '')}\n"
            f"Summary: {art.get('summary', '')}"
        )
        if len(art_content) > 100:
            kb_docs.append(Document(
                page_content=art_content, 
                metadata={"source": "json_kb", "section": "articles", "category": "article"}
            ))

    # Handle feedback as a single doc
    feedback = data.get("feedback", "")
    if len(feedback) > 100:
        kb_docs.append(Document(
            page_content=f"Feedback Section: {feedback}", 
            metadata={"source": "json_kb", "section": "feedback", "category": "user_feedback"}
        ))

    # Skip faqs to avoid duplication with CSV

    print(f"✅ Loaded {len(kb_docs)} structured entries from JSON KB (skipped faqs)")
    return kb_docs

# ------------------------
# Chunk Documents
# ------------------------
def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    all_chunks = []
    for doc in documents:
        chunks = splitter.split_documents([doc])
        all_chunks.extend([chunk for chunk in chunks if len(chunk.page_content) > 100])
    print(f"✅ Created {len(all_chunks)} chunks from {len(documents)} docs (after filtering shorts)")
    return all_chunks

# ------------------------
# Setup Chroma Vector Store
# ------------------------
def setup_vector_store(documents):
    embedding_function = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    client_settings = chromadb.Settings(
        persist_directory=CHROMA_PATH,
        is_persistent=True
    )

    # Chunk first
    chunked_docs = chunk_documents(documents)

    vector_store = Chroma.from_documents(
        collection_name="ai_knowledge",
        documents=chunked_docs,
        embedding=embedding_function,
        client_settings=client_settings
    )

    print(f"✅ Vector store created with {len(chunked_docs)} total chunks")
    return vector_store

# ------------------------
# Main
# ------------------------
def main():
    all_docs = []

    # Load JSON
    try:
        print("📥 Loading JSON Knowledge Base...")
        kb_docs = load_json_kb(JSON_PATH)
        all_docs.extend(kb_docs)
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")

    if not all_docs:
        print("❌ No documents found. Exiting.")
        return

    # Dedup across sources (simple content hash)
    seen = set()
    unique_docs = []
    for doc in all_docs:
        content_hash = hash(doc.page_content)
        if content_hash not in seen:
            seen.add(content_hash)
            unique_docs.append(doc)
    all_docs = unique_docs
    print(f"✅ After cross-source dedup: {len(all_docs)} unique docs")

    # Setup vector store
    try:
        print("⚙️ Setting up the vector store...")
        setup_vector_store(all_docs)
        print(f"✅ Vector store setup completed successfully in {CHROMA_PATH}.")
    except Exception as e:
        print(f"❌ Error setting up vector store: {e}")

if __name__ == "__main__":
    main()