import re
import gradio as gr
import os
from functools import lru_cache

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Load PDF
print("Loading document...")
loader = PyMuPDFLoader("./regles-du-rugby.pdf") # le document a 216 pages
documents = loader.load()
print(f"Loaded {len(documents)} documents.")

# Split - chunks 
print("Splitting document into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(documents)
print(f"Created {len(chunks)} chunks.")

# Embeddings & LLM optimisés
print("Setting up embeddings and LLM...")
embedding_function = OllamaEmbeddings(
    model="nomic-embed-text", 
    base_url=OLLAMA_BASE_URL
)


llm = OllamaLLM(
    model="llama3.2",  
    base_url=OLLAMA_BASE_URL,
    temperature=0.1,  # Réduit la créativité pour plus de rapidité
)

# Vector store avec persistance
print("Loading or creating vector store...")
if os.path.exists("./chroma_db"):
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embedding_function,
        collection_name="rugby_RAG"
    )
    print("Vector store loaded from disk.")
else:
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        collection_name="rugby_RAG",
        persist_directory="./chroma_db"
    )
    print("Vector store created.")

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}  # Réduit de 4 à 3
)

# Cache pour questions répétées
@lru_cache(maxsize=50)
def cached_retrieval(question):
    docs = retriever.invoke(question)
    return "\n\n".join(doc.page_content for doc in docs)

# RAG pipeline optimisé
def ask_question(question):
    context = cached_retrieval(question)

    # Prompt plus concis
    prompt = f"""Réponds brièvement à la question en utilisant uniquement ce contexte. Si la réponse n'est pas dans le contexte, dis "Je ne sais pas".

Contexte: {context}

Question: {question}

Réponse:"""

    response = llm.invoke(prompt)
    
    # Nettoyage
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
    return response

# Gradio UI
interface = gr.Interface(
    fn=ask_question,
    inputs=gr.Textbox(label="Votre question", placeholder="Ex: Qu'est-ce qu'un essai au rugby ?"),
    outputs=gr.Textbox(
        label="Réponse", 
        placeholder="La réponse apparaîtra ici...",     
        lines=10, 
        ),
    title="🏉 RAG Chatbot: Guide du Rugby",
    description="Posez vos questions sur le rugby. Par Christian et Omar | Alimenté par Llama 3.2",
    examples=[
        ["Qu'est-ce que le rugby ?"],
        ["Combien de joueurs dans une équipe ?"],
        ["Quelles sont les règles principales ?"]
    ]
)

print("Launching interface...")
interface.launch(server_name="0.0.0.0", server_port=7860, share=False)