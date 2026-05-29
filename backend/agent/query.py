import os
from dotenv import load_dotenv
from anthropic import Anthropic
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()

os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma")
CACHE_DIR = os.path.join(BASE_DIR, "data", "embeddings_cache")

COLLECTION_MAP = {
    "drilling": "drilling_docs",
    "refinery": "refinery_docs",
    "guidelines": "guidelines_docs"
}

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=CACHE_DIR
)

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model_name = os.getenv("MODEL_NAME")


def run_query_pipeline(domain: str, keyword: str, prompt: str) -> dict:
    collection_name = COLLECTION_MAP.get(domain)
    if not collection_name:
        raise ValueError(f"Unsupported domain: {domain}")

    try:
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=CHROMA_PATH
        )

        query = f"{keyword} {prompt}"
        results_with_scores = vectorstore.similarity_search_with_score(query, k=5)
        retrieved_chunks = [doc.page_content for doc, score in results_with_scores]

        guidelines_store = Chroma(
            collection_name=COLLECTION_MAP["guidelines"],
            embedding_function=embeddings,
            persist_directory=CHROMA_PATH
        )
        guidelines_chunks = [doc.page_content for doc in guidelines_store.similarity_search(prompt, k=2)]

        chunks_text = "\n\n".join(retrieved_chunks)
        guidelines_text = "\n\n".join(guidelines_chunks)

        system_prompt = """
        You are an expert diagnostic assistant for oil and gas field engineers.
        Be concise and precise. Use the provided documentation to inform your response.
        """

        final_prompt = f"""
        Equipment: {keyword}
        Engineer Issue: {prompt}

        Relevant Equipment Documentation:
        {chunks_text}

        Safety Guidelines:
        {guidelines_text}

        Provide a precise diagnostic response including:
        - Root cause analysis
        - Step by step corrective actions aligned with safety guidelines
        - Part replacement recommendation with part number if applicable
        - Inventory and procurement details if replacement is needed
        Format as numbered steps. Be concise.
        If the keyword is not found in the documentation, say you have no relevant information about the equipment mentioned.
        Don't provide anything that is not supported by the documentation. Always include safety compliance notes.
        Keep it user friendly. If you don't know the answer, say you don't know.
        The engineer is likely in a high pressure situation and needs clear actionable guidance.
        The display of text should be easy to read and not so high level that it confuses the engineer.
        The goal is to help them understand the issue and how to resolve it quickly.
        """

        response = client.messages.create(
            model=model_name,
            max_tokens=1500,
            temperature=0.5,
            system=system_prompt,
            messages=[{"role": "user", "content": final_prompt}]
        )
        response_text = response.content[0].text.strip()

        procurement_needed = any(
            word in response_text.lower()
            for word in ["replace", "replacement", "part number", "order", "procurement"]
        )

        # Confidence scoring
        confidence_prompt = f"""
        You are evaluating a technical diagnostic response for oil and gas equipment.
        Score from 0 to 10 how well this response addresses the engineer's query.
        - 9-10: Complete answer with specific steps, part numbers, safety notes
        - 6-8: Partial answer, missing some details
        - 3-5: Vague answer, lacks specifics
        - 0-2: Does not address the query

        Query: {prompt}
        Response: {response_text[:300]}

        Reply with ONLY a number between 0 and 10. Nothing else.
        """

        try:
            confidence_response = client.messages.create(
                model=model_name,
                max_tokens=10,
                temperature=0.0,
                messages=[{"role": "user", "content": confidence_prompt}]
            )
            confidence = float(confidence_response.content[0].text.strip())
            confidence = max(0.0, min(10.0, confidence))
        except:
            confidence = 5.0

        return {
            "response": response_text,
            "confidence": confidence,
            "procurement_needed": procurement_needed,
            "sources": retrieved_chunks
        }

    except Exception as e:
        raise Exception(f"Query pipeline failed: {e}")