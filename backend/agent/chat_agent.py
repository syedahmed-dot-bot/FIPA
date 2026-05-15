import os
from urllib import response
from dotenv import load_dotenv


from anthropic import Anthropic

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma")

COLLECTION_MAP = {
    "drilling": "drilling_docs",
    "refinery": "refinery_docs",
    "guidelines": "guidelines_docs"
}

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model_name = os.getenv("MODEL_NAME")


def run_chat_agent(message: str, domain: str, conversation_history: list) -> dict:
    collection_name = COLLECTION_MAP.get(domain)
    if not collection_name:
        raise ValueError(f"Unsupported domain: {domain}")

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )

    results_with_scores = vectorstore.similarity_search_with_relevance_scores(message, k=5)
    retrieved_chunks = [doc.page_content for doc, score in results_with_scores]
    scores = [score for doc, score in results_with_scores]
    confidence = round(sum(scores) / len(scores), 2) if scores else 0.0

    guidelines_store = Chroma(
        collection_name=COLLECTION_MAP["guidelines"],
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )
    guidelines_chunks = [doc.page_content for doc in guidelines_store.similarity_search(message, k=2)]

    chunks_text = "\n\n".join(retrieved_chunks)
    guidelines_text = "\n\n".join(guidelines_chunks)

    prompt = f"""
    Engineer Query: {message}

    Relevant Equipment Documentation:
    {chunks_text}

    Relevant Safety Guidelines:
    {guidelines_text}

    Provide a precise diagnostic response. Include:
    - Root cause of the issue
    - Step by step corrective actions
    - Safety compliance notes from guidelines
    - Part replacement recommendation if applicable
    Format as numbered steps. Maximum 500 tokens.
    """

    response = client.messages.create(
        model=model_name,
        max_tokens=1000,
        temperature=0.1,
        system="You are an expert diagnostic assistant for oil and gas field engineers. Be concise and precise.",
        messages=conversation_history + [{"role": "user", "content": prompt}]
    )

    return {
        "response": response.content[0].text.strip(),
        "confidence": confidence,
        "sources": retrieved_chunks
    }