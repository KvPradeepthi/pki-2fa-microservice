#!/usr/bin/env python3
import os
import base64
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import pyotp
import time

app = FastAPI()

PRIVATE_KEY_PATH = "/app/student_private.pem"
SEED_PATH = "/data/seed.txt"

def load_private_key():
    with open(PRIVATE_KEY_PATH, 'rb') as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )

def decrypt_seed(encrypted_seed_b64: str) -> str:
    try:
        encrypted_bytes = base64.b64decode(encrypted_seed_b64)
        private_key = load_private_key()
        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        seed = decrypted_bytes.decode('utf-8')
        if len(seed) != 64 or not all(c in '0123456789abcdef' for c in seed):
            raise ValueError("Invalid seed format")
        return seed
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")

def get_totp_code(hex_seed: str):
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    totp = pyotp.TOTP(base32_seed, interval=30)
    code = totp.now()
    current_time = int(time.time())
    time_remaining = 30 - (current_time % 30)
    return code, time_remaining

class DecryptSeedRequest(BaseModel):
    encrypted_seed: str

class Verify2FARequest(BaseModel):
    code: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/decrypt-seed")
async def decrypt_seed_endpoint(request: DecryptSeedRequest):
    try:
        seed = decrypt_seed(request.encrypted_seed)
        Path("/data").mkdir(parents=True, exist_ok=True)
        with open(SEED_PATH, 'w') as f:
            f.write(seed)
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")

@app.get("/generate-2fa")
async def generate_2fa():
    try:
        if not os.path.exists(SEED_PATH):
            raise HTTPException(status_code=500, detail="Seed not decrypted yet")
        with open(SEED_PATH, 'r') as f:
            seed = f.read().strip()
        code, valid_for = get_totp_code(seed)
        return {"code": code, "valid_for": valid_for}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

@app.post("/verify-2fa")
async def verify_2fa(request: Verify2FARequest):
    try:
        if not request.code:
            raise HTTPException(status_code=400, detail="Missing code")
        if not os.path.exists(SEED_PATH):
            raise HTTPException(status_code=500, detail="Seed not decrypted yet")
        with open(SEED_PATH, 'r') as f:
            seed = f.read().strip()
        seed_bytes = bytes.fromhex(seed)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        totp = pyotp.TOTP(base32_seed, interval=30)
        is_valid = totp.verify(request.code, valid_window=1)
        return {"valid": is_valid}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
