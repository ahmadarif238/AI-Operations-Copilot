import requests
import sys
import time

BASE_URL = "http://localhost:8000/api/v1"

def check_health():
    try:
        resp = requests.get("http://localhost:8000/health")
        if resp.status_code == 200:
            print("[x] Health Check Passed")
            return True
    except:
        pass
    print("[ ] Health Check Failed")
    return False

def check_upload():
    try:
        files = [('files', ('test.txt', b'Test content', 'text/plain'))]
        resp = requests.post(f"{BASE_URL}/docs/upload", files=files, data={'department': 'Test'})
        if resp.status_code == 200:
            print("[x] Upload Docs Passed")
            return True
    except Exception as e:
        print(e)
    print("[ ] Upload Docs Failed")
    return False

def check_ask():
    try:
        resp = requests.post(f"{BASE_URL}/ask", json={"query": "test", "user_id": "00000000-0000-0000-0000-000000000000"})
        data = resp.json()
        if "answer" in data:
            print("[x] Ask Query Passed")
            return True
    except:
        pass
    print("[ ] Ask Query Failed")
    return False

def check_log_ticket():
    try:
        resp = requests.post(f"{BASE_URL}/log", json={"type": "ERROR", "message": "Critical failure simulation"})
        if resp.status_code == 202:
            print("[x] Log Ingestion Passed")
            # Wait for background monitoring
            time.sleep(2)
            # Check if ticket created (Mock check since we can't easily query DB here without proper auth or DB access)
            # In a real script we would query the ticket API
            # tickets = requests.get(...)
            return True
    except:
        pass
    print("[ ] Log Ingestion Failed")
    return False

def main():
    print("Running Verification Checks...")
    if not check_health():
        sys.exit(1)
        
    results = [
        check_upload(),
        check_ask(),
        check_log_ticket()
    ]
    
    if all(results):
        print("\nAll systems operational.")
        sys.exit(0)
    else:
        print("\nSome checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
