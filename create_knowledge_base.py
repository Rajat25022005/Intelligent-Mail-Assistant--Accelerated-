import chromadb
from pathlib import Path

client = chromadb.PersistentClient(path="my_knowledge_base")
collection = client.get_or_create_collection(name="personal_knowledge")

try:
    # Get the directory where the script is located
    script_dir = Path(__file__).parent
    # Create a full, absolute path to my_notes.txt
    file_path = script_dir / 'my_notes.txt'

    # This new print statement will show you the EXACT path it's trying to use.
    print(f"Attempting to read knowledge base file from: {file_path}")

    with open(file_path, 'r') as f:
        # Read all lines from the file
        documents = [line.strip() for line in f.readlines() if line.strip()]

except FileNotFoundError:
    print(f"ERROR: File not found at {file_path}")
    print("Please make sure 'my_notes.txt' is in the same folder as your 'create_knowledge_base.py' script.")
    documents = [] # Ensure documents is an empty list on error

# This print statement will now have the correct count
print(f"Adding {len(documents)} documents to the collection...")

# This will now throw the ValueError if the file was truly not found
# and the documents list is empty.
collection.add(
    documents=documents,
    ids=[f"doc_{i}" for i in range(len(documents))]
)

print("\nKnowledge base created successfully.")
print(f"Total documents in collection: {collection.count()}")