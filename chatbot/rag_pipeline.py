# rag_pipeline.py
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "AI FAQ"

# Vector store path
CHROMA_PATH = "data1/ai"

# ------------------------
# Load Vector Store
# ------------------------
def load_vector_store():
    embedding_function = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = Chroma(
        collection_name="ai_knowledge",
        embedding_function=embedding_function,
        persist_directory=CHROMA_PATH
    )

    if vector_store._collection.count() == 0:
        raise ValueError(f"No data found in ChromaDB at {CHROMA_PATH}. Run embed.py first.")

    return vector_store

# ------------------------
# Initialize LLM
# ------------------------
def setup_generator():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7
    )
    return llm

# ------------------------
# Create Classifier (Casual vs Knowledge)
# ------------------------
def create_classifier(llm):
    classifier_prompt = PromptTemplate.from_template("""
    Classify this user message as either 'casual' (general chit-chat like greetings, how are you, opinions) 
    or 'knowledge' (questions about AI, company, solutions, events, etc.).
    Respond only with: CASUAL or KNOWLEDGE.
    Message: {input}
    """)
    chain = classifier_prompt | llm | StrOutputParser()
    return chain

# ------------------------
# Create RAG Pipeline
# ------------------------
def create_rag_pipeline():
    # Setup LLM & vector store
    llm = setup_generator()
    vector_store = load_vector_store()

    # History-aware retriever prompt
    context_q_system_prompt = """
    Given a chat history and the latest user question which might reference context in chat history, 
    formulate a standalone question which can be understood without the chat history. 
    Do not answer the question, just formulate it if needed and otherwise return as it is.
    """
    context_q_prompt = ChatPromptTemplate.from_messages([
        ("system", context_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])

    # QA prompt with professional company persona
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", """I'm a dedicated member of the AI Solutions team—your trusted guide to cutting-edge AI innovations that drive real business impact. 

Respond based EXCLUSIVELY on the provided context. If information isn't available, redirect politely and suggest next steps.

Maintain a professional, warm tone:
- Speak as a company insider: "At AI Solutions, we..." or "Our team specializes in..."
- Keep it concise, structured, engaging.
- Conclude with a thoughtful question or next step.
- Emojis sparingly.

Context: {context}"""),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])

    # Retriever and RAG chain
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )
    history_aware_retriever = create_history_aware_retriever(llm, retriever, context_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return rag_chain, llm

# ------------------------
# Create Casual Chain
# ------------------------
def create_casual_chain():
    llm = setup_generator()
    casual_prompt = ChatPromptTemplate.from_messages([
        ("system", """As a proud AI Solutions team member, respond to casual queries with professional poise and genuine warmth—like a colleague sharing insights over coffee. Keep it brief, polished, and tied to our world of innovation. End with an inviting question linking back to our services.

Examples: 
- "How are you?" → "I'm thriving here at AI Solutions—fueled by the thrill of transformative tech! How about you—what's sparking your interest in AI today?"
- "What's up?" → "All systems go on innovative projects. At AI Solutions, we're always exploring new horizons. What's on your mind—perhaps our latest FinTech solutions?"

Be supportive, expert, and subtly promotional."""),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])
    casual_chain = casual_prompt | llm | StrOutputParser()
    return casual_chain, llm

# ------------------------
# Utility to run RAG query
# ------------------------
def run_rag_query(rag_chain, query, chat_history):
    response = rag_chain.invoke({
        "input": query,
        "chat_history": chat_history
    })
    return response["answer"]
