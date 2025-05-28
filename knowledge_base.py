import chromadb
from sentence_transformers import SentenceTransformer

# 1. Initialize ChromaDB client and create a collection
client = chromadb.Client()
# Use SentenceTransformer for creating embeddings locally
# Or, you can use `client = chromadb.PersistentClient(path="/path/to/db")` to save to disk
collection = client.get_or_create_collection(name="personal_knowledge")

print("Reading knowledge base file...")
# 2. Read the text file and split it into "documents" (by line)
with open('my_notes.txt', 'r') as f:
    documents = [line.strip() for line in f.readlines() if line.strip()]

# 3. Generate a unique ID for each document
ids = [f"doc_{i}" for i in range(len(documents))]

print(f"Adding {len(documents)} documents to the collection...")
# 4. Add the documents to the ChromaDB collection
# ChromaDB will automatically use its default embedding model if not specified,
# but explicitly using SentenceTransformer is good practice.
collection.add(
    documents=documents,
    ids=ids
)

print("\nKnowledge base created successfully.")
print(f"Total documents in collection: {collection.count()}")