# scripts/index_txts.py
import os
import glob
import ollama
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

# --- QDRANT CLOUD ---
QDRANT_URL = "https://9ee1de95-6221-4798-83e2-fe52e1480865.eu-central-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NDRiNzNhMjItZDE3MC00OTkzLTk3MTAtNDZiMDg0N2JhNDMyIn0.E6zmo4cUxYDAhHSqtRYMXKvLRz-_N4kbauVzGQwAgkc"

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

EMBED_MODEL = "bge-m3"
COLLECTION = "reglements_universitaires"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "documents")  # <-- SEULEMENT documents/

def get_embedding(text):
    return ollama.embed(model=EMBED_MODEL, input=text)["embeddings"][0]

if client.collection_exists(collection_name=COLLECTION):
    client.delete_collection(collection_name=COLLECTION)

client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
)

points = []
point_id = 0

# Cherche UNIQUEMENT dans documents/, pas dans venv/
txt_files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
print(f"Trouvé {len(txt_files)} fichiers .txt :")
for fp in txt_files:
    print(" -", os.path.relpath(fp, BASE_DIR))

for filepath in txt_files:
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = [c.strip() for c in content.split("Article") if c.strip()]
    for chunk in chunks:
        full_text = "Article" + chunk
        vector = get_embedding(full_text)
        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload={"text": full_text, "source": filename}
            )
        )
        point_id += 1
        print(f"Ajouté : {filename} - {full_text[:40]}...")

client.upsert(collection_name=COLLECTION, points=points)
print(f"\nTerminé ! {len(points)} chunks ingérés dans Qdrant Cloud avec {EMBED_MODEL}.")
