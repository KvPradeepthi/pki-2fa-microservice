#!/usr/bin/env python3
import requests
import json

def request_seed(student_id: str, github_repo_url: str):
    with open('student_public.pem', 'r') as f:
        public_key = f.read()
    
    url = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws/"
    payload = {
        "student_id": 23A91A1225,
        "github_repo_url": https://github.com/KvPradeepthi/pki-2fa-microservice,
        "public_key": public_key
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    
    if data.get("status") == "success":
        with open('encrypted_seed.txt', 'w') as f:
            f.write(data["encrypted_seed"])
        print("✓ Encrypted seed saved to encrypted_seed.txt")
    else:
        print("✗ Failed to get encrypted seed")
        print(data)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 request_seed.py <student_id> <github_repo_url>")
        sys.exit(1)
    
    student_id = sys.argv[1]
    github_repo_url = sys.argv[2]
    request_seed(student_id, github_repo_url)
