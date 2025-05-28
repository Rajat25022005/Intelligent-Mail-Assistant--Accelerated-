import chromadb

client = chromadb.PersistentClient(path="my_knowledge_base")


# Now, instead of get_collection, it's safer to use get_or_create_collection
# This won't cause an error if the collection doesn't exist yet.
collection = client.get_or_create_collection(name="personal_knowledge")

def query_rag(query_text):
    """Queries the RAG knowledge base for relevant documents."""
    # Query the collection
    results = collection.query(
        query_texts=[query_text],
        n_results=2  # Ask for the top 2 most relevant results
    )
    return results['documents'][0]


if __name__ == "__main__":
    # --- Test Queries ---
    query1 = "who is the contact for project phoenix?"
    print(f"Query: {query1}")
    retrieved_docs1 = query_rag(query1)
    print("Retrieved Context:")
    for doc in retrieved_docs1:
        print(f"- {doc}")

    print("\n" + "-"*30 + "\n")

    query2 = "what is my frequent flyer number"
    print(f"Query: {query2}")
    retrieved_docs2 = query_rag(query2)
    print("Retrieved Context:")
    for doc in retrieved_docs2:
        print(f"- {doc}")