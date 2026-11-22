# scripts/chatbot.py
import ollama
from qdrant_client import QdrantClient

# --- QDRANT CLOUD - MEME QUE DANS index_txts.py ---
QDRANT_URL = "https://9ee1de95-6221-4798-83e2-fe52e1480865.eu-central-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NDRiNzNhMjItZDE3MC00OTkzLTk3MTAtNDZiMDg0N2JhNDMyIn0.E6zmo4cUxYDAhHSqtRYMXKvLRz-_N4kbauVzGQwAgkc"

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

EMBED_MODEL = "bge-m3"
LLM_MODEL = "llama3.2:3b"
COLLECTION = "reglements_universitaires"

def get_embedding(text):
    return ollama.embed(model=EMBED_MODEL, input=text)["embeddings"][0]

def rag_answer(question):
    # 1. Transforme la question en vecteur
    q_vector = get_embedding(question)

    # 2. Cherche dans Qdrant Cloud - SANS using="dense"
    results = client.query_points(
        collection_name=COLLECTION,
        query=q_vector,
        limit=3,
        with_payload=True
    ).points

    # 3. Construit le contexte
    context = "\n\n".join([r.payload["text"] for r in results])
    sources = ", ".join(set([r.payload["source"] for r in results]))

    # 4. Prompt anti-hallucination
    prompt = f"""Tu es un assistant de la Faculté des Sciences Ain Chock.
Réponds UNIQUEMENT en utilisant le contexte ci-dessous.
Si la réponse n'est pas dans le contexte, dis : "Je ne trouve pas cette information dans les règlements."
Réponds en français, de façon claire et concise.

Contexte :
{context}

Question : {question}
Réponse :"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    return f"{response['message']['content']}\n\n📚 Sources : {sources}"

print("🎓 Chatbot RAG bge-m3 - Qdrant Cloud (tape 'exit' pour quitter)")
while True:
    q = input("\nQuestion : ")
    if q.lower() in ["exit", "quit", "q"]:
        break
    print("\nRéponse :", rag_answer(q))
