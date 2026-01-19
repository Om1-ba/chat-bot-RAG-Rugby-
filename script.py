import re
import gradio as gr

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM

# Load PDF
print("Loading document...")
loader = PyMuPDFLoader("C:/Users/ebam/Desktop/MES_DOSSIERS/UTT/MLOps/Comprendre-le-rugby.pdf")
documents = loader.load()
print(f"Loaded {len(documents)} documents.")

# Split
print("Splitting document into chunks...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)
print(f"Created {len(chunks)} chunks.")

# Embeddings & LLM
print("Setting up embeddings and LLM...")
embedding_function = OllamaEmbeddings(model="nomic-embed-text")
llm = OllamaLLM(model="deepseek-r1")

# Vector store
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_function,
    collection_name="foundations_of_llms",
    persist_directory="./chroma_db"
)
print("Vector store created.")

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# RAG pipeline
def ask_question(question):
    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
You are a helpful assistant.
Answer the question using ONLY the context below.
If the answer is not in the context, say you don't know.

Context:
{context}

Question:
{question}
"""

    response = llm.invoke(prompt)

    # Remove DeepSeek thinking traces
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
    return response

# Gradio UI
interface = gr.Interface(
    fn=ask_question,
    inputs="text",
    outputs="text",
    title="RAG Chatbot: Comprehensive Guide to Rugby",
    description="Ask questions about the Comprehensive Guide to Rugby book. Made by Christian and Omar. Powered by DeepSeek-R1."
)
print("Launching interface...")
interface.launch(share=True, inbrowser=True)
