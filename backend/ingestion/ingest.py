import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DRILLING_PATH = os.path.join(BASE_DIR, "data", "raw_documents", "drilling")
REFINERY_PATH = os.path.join(BASE_DIR, "data", "raw_documents", "refinery")
GUIDELINES_PATH = os.path.join(BASE_DIR, "data", "raw_documents", "guidelines")
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def ingest_drilling_documents():
    drilling_loader = PyPDFDirectoryLoader(DRILLING_PATH)
    drilling_docs = drilling_loader.load()
    drilling_chunks = text_splitter.split_documents(drilling_docs)
    Chroma.from_documents(
        drilling_chunks,
        embeddings,
        collection_name="drilling_docs",
        persist_directory=CHROMA_PATH
    )
    print(f"Drilling ingestion complete. {len(drilling_chunks)} chunks stored.")

def ingest_refiner_documents():
    refinery_loader = PyPDFDirectoryLoader(REFINERY_PATH)
    refinery_docs = refinery_loader.load()
    refinery_chunks = text_splitter.split_documents(refinery_docs)
    Chroma.from_documents(
        refinery_chunks,
        embeddings,
        collection_name="refinery_docs",
        persist_directory=CHROMA_PATH
    )
    print(f"Refinery ingestion complete. {len(refinery_chunks)} chunks stored.")

def ingest_guidelines_documents():
    guidelines_loader = PyPDFDirectoryLoader(GUIDELINES_PATH)
    guidelines_docs = guidelines_loader.load()
    guidelines_chunks = text_splitter.split_documents(guidelines_docs)
    Chroma.from_documents(
        guidelines_chunks,
        embeddings,
        collection_name="guidelines_docs",
        persist_directory=CHROMA_PATH
    )
    print(f"Guidelines ingestion complete. {len(guidelines_chunks)} chunks stored.")

if __name__ == "__main__":
    print("Ingesting drilling documents...")
    ingest_drilling_documents()
    print("\nIngesting refinery documents...")
    ingest_refiner_documents()
    print("\nIngesting guidelines documents...")
    ingest_guidelines_documents()
    print("\nAll documents ingested successfully.")
