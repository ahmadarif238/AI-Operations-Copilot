
import os

ENV_PATH = ".env"
NEW_DB_URL = "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aiops"

def fix_env():
    if not os.path.exists(ENV_PATH):
        print(".env not found!")
        return

    with open(ENV_PATH, "r") as f:
        lines = f.readlines()

    found = False
    new_lines = []
    for line in lines:
        if line.strip().startswith("DATABASE_URL="):
            new_lines.append(NEW_DB_URL + "\n")
            found = True
        else:
            new_lines.append(line)
    
    if not found:
        new_lines.append("\n" + NEW_DB_URL + "\n")
    
    with open(ENV_PATH, "w") as f:
        f.writelines(new_lines)
    print("Updated DATABASE_URL in .env")

if __name__ == "__main__":
    fix_env()
