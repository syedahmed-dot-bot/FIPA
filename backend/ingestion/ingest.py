import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
from pinecone import Pinecone

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DRILLING_PATH = os.path.join(BASE_DIR, "data", "raw_documents", "drilling")
REFINERY_PATH = os.path.join(BASE_DIR, "data", "raw_documents", "refinery")
GUIDELINES_PATH = os.path.join(BASE_DIR, "data", "raw_documents", "guidelines")

CACHE_DIR = os.path.join(BASE_DIR, "data", "embeddings_cache")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200
)

embeddings = PineconeEmbeddings(
    model="multilingual-e5-large",
    pinecone_api_key=os.getenv("PINECONE_API_KEY")
)

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX")

def ingest_documents(folder_path: str, namespace: str):
    print(f"\nIngesting {namespace}...")
    loader = PyPDFDirectoryLoader(folder_path)
    docs = loader.load()
    chunks = text_splitter.split_documents(docs)
    PineconeVectorStore.from_documents(
        chunks,
        embeddings,
        index_name=index_name,
        namespace=namespace
    )
    print(f"{namespace} complete. {len(chunks)} chunks stored.")

if __name__ == "__main__":
    print("Starting ingestion pipeline...")
    ingest_documents(DRILLING_PATH, "drilling-docs")
    ingest_documents(REFINERY_PATH, "refinery-docs")
    ingest_documents(GUIDELINES_PATH, "guidelines-docs")
    print("\nIngestion complete.")