import os
import sys
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec, PodSpec

# Load env from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.core.config import settings

def check_and_fix():
    api_key = settings.PINECONE_API_KEY
    index_name = settings.PINECONE_INDEX_NAME or "ai-ops"
    
    if not api_key:
        print("Error: PINECONE_API_KEY not found in settings.")
        return

    pc = Pinecone(api_key=api_key)
    
    print(f"Checking index '{index_name}'...")
    active_indexes = [i.name for i in pc.list_indexes()]
    
    if index_name not in active_indexes:
        print(f"Index '{index_name}' does not exist. Attempting to create...")
        create_index(pc, index_name)
    else:
        # Check details
        idx_info = pc.describe_index(index_name)
        dim = idx_info.dimension
        print(f"Current Dimension: {dim}")
        
        if dim != 384:
            print(f"MISMATCH! Model needs 384, Index has {dim}.")
            print("Deleting and recreating index...")
            try:
                pc.delete_index(index_name)
                print("Deleted old index.")
                create_index(pc, index_name)
            except Exception as e:
                print(f"Error recreating index: {e}")
        else:
            print("Dimension matches (384). Everything looks good!")

def create_index(pc, name):
    # Try Serverless (AWS us-east-1 is common free tier)
    # Or try default spec from env/config if available
    # Using a generic fallback strategy
    
    try:
        print(f"Creating index '{name}' with dimension 384...")
        pc.create_index(
            name=name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print("Index created successfully (Serverless AWS).")
    except Exception as e:
        print(f"Failed to create Serverless index: {e}")
        print("Trying gcp-starter (old free tier)...")
        try:
            pc.create_index(
                name=name,
                dimension=384,
                metric="cosine",
                spec=PodSpec(
                    environment="gcp-starter"
                )
            )
            print("Index created successfully (Pod GCP).")
        except Exception as e2:
             print(f"Failed to create Pod index: {e2}")
             print("Please create manually in console: Name='ai-ops', Dim=384, Metric='cosine'.")

if __name__ == "__main__":
    check_and_fix()
