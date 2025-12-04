#!/usr/bin/env python3
import subprocess
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

def get_commit_hash():
    result = subprocess.run(['git', 'log', '-1', '--format=%H'], 
                          capture_output=True, text=True)
    return result.stdout.strip()

def sign_message(message: str, private_key_path: str):
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
    
    signature = private_key.sign(
        message.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def encrypt_signature(signature, public_key_path: str):
    with open(public_key_path, 'rb') as f:
        public_key = serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )
    
    encrypted = public_key.encrypt(
        signature,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted

def main():
    commit_hash = get_commit_hash()
    print(f"Commit Hash: {commit_hash}")
    
    signature = sign_message(commit_hash, "student_private.pem")
    encrypted_sig = encrypt_signature(signature, "instructor_public.pem")
    encrypted_sig_b64 = base64.b64encode(encrypted_sig).decode('utf-8')
    
    print(f"Encrypted Signature: {encrypted_sig_b64}")
    
    with open('submission_proof.txt', 'w') as f:
        f.write(f"Commit Hash: {commit_hash}\n")
        f.write(f"Encrypted Signature: {encrypted_sig_b64}\n")

if __name__ == "__main__":
    main()
