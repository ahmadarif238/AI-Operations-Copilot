import os

def update_env():
    env_path = ".env"
    if not os.path.exists(env_path):
        print(".env not found")
        return

    with open(env_path, "r") as f:
        content = f.read()

    new_content = content.replace('PINECONE_INDEX_NAME="ai-ops"', 'PINECONE_INDEX_NAME="ai-ops-v2"')
    new_content = new_content.replace('PINECONE_INDEX_NAME=ai-ops', 'PINECONE_INDEX_NAME=ai-ops-v2')
    
    # Check if replaced
    if "ai-ops-v2" not in new_content:
        # Maybe it's not there or different format, append it
        if "PINECONE_INDEX_NAME" not in content:
            new_content += '\nPINECONE_INDEX_NAME="ai-ops-v2"\n'
        else:
            print("Could not safely replace index name. Check file format.")
            print(content)
            return

    with open(env_path, "w") as f:
        f.write(new_content)
    
    print("Updated .env successfully.")

if __name__ == "__main__":
    update_env()
