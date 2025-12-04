#!/usr/bin/env python3
import os
from datetime import datetime
import pyotp
import base64

SEED_PATH = "/data/seed.txt"

def main():
    try:
        if not os.path.exists(SEED_PATH):
            return
        
        with open(SEED_PATH, 'r') as f:
            seed = f.read().strip()
        
        seed_bytes = bytes.fromhex(seed)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        totp = pyotp.TOTP(base32_seed, interval=30)
        code = totp.now()
        
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} - 2FA Code: {code}"
        print(log_line)
    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    main()
