import chromadb
import os

try:
    client = chromadb.PersistentClient(path="/Users/kaancatalkaya/Desktop/Projects/Google Ads - mondaybrew/backend/knowledge_base/chroma_db")
    collection = client.get_collection("agency_knowledge")
    count = collection.count()
    print(f"Document count: {count}")
except Exception as e:
    print(f"Error: {e}")
