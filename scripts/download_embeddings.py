from sentence_transformers import SentenceTransformer
import os

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", "data", "embeddings_cache")

os.makedirs(CACHE_DIR, exist_ok=True)

print(f"Downloading embedding model to {CACHE_DIR}...")
model = SentenceTransformer(MODEL_NAME, cache_folder=CACHE_DIR)
print("Embedding model downloaded and cached successfully.")