# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_pipeline import create_rag_pipeline, create_casual_chain, create_classifier, run_rag_query
from langchain_core.messages import HumanMessage, AIMessage

# ------------------------
# FastAPI Setup
# ------------------------
app = FastAPI(title="AI Solutions Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# Initialize RAG, Casual Chain, and Classifier
# ------------------------
rag_chain, llm_rag = create_rag_pipeline()
casual_chain, llm_casual = create_casual_chain()
classifier = create_classifier(llm_rag)  # use same LLM for classification
chat_history = []

# ------------------------
# Request/Response Models
# ------------------------
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

# ------------------------
# Routes
# ------------------------
@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    global chat_history

    user_query = request.query.strip()
    if not user_query:
        return QueryResponse(response="Please enter a valid message.")

    # Append user message
    chat_history.append(HumanMessage(content=user_query))

    # Classify query
    try:
        classification = classifier.invoke({"input": user_query}).strip().upper()
    except Exception:
        classification = "KNOWLEDGE"  # fallback

    # Generate response
    try:
        if classification == "CASUAL":
            answer = casual_chain.invoke({
                "input": user_query,
                "chat_history": chat_history[-4:]  # last few messages
            })
        else:
            answer = run_rag_query(rag_chain, user_query, chat_history[-10:])
    except Exception:
        answer = "I'm having trouble processing that—let's try another question!"

    # Append AI response
    chat_history.append(AIMessage(content=answer))

    # Trim chat history to prevent token overflow
    if len(chat_history) > 20:
        chat_history = chat_history[-20:]

    return QueryResponse(response=answer)

@app.post("/reset")
async def reset_chat():
    global chat_history
    chat_history = []
    return {"status": "chat reset"}
