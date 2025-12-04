# 🚀 PKI 2FA Microservice - Complete Setup Guide

## Prerequisites
Make sure you have installed:
- Python 3.8+
- Docker & Docker Compose
- Git
- curl (for testing)
- wget or similar download tool

## Complete Setup Instructions

### STEP 1: Clone Repository
```bash
git clone https://github.com/KvPradeepthi/pki-2fa-microservice.git
cd pki-2fa-microservice
```

### STEP 2: Download Instructor Public Key
```bash
wget https://partnr-public.s3.us-east-1.amazonaws.com/gpp-resources/instructor_public.pem
ls -la instructor_public.pem
git add instructor_public.pem
git commit -m "Add instructor public key"
git push origin main
```

### STEP 3: Generate Your RSA Key Pair
```bash
python3 keygen.py
ls -la student_*.pem
git add student_private.pem student_public.pem
git commit -m "Add student RSA key pair"
git push origin main
```

### STEP 4: Request Encrypted Seed from API
```bash
# IMPORTANT: Replace YOUR_STUDENT_ID with your actual student ID
python3 request_seed.py YOUR_STUDENT_ID https://github.com/KvPradeepthi/pki-2fa-microservice

# Verify file created
ls -la encrypted_seed.txt
cat encrypted_seed.txt

# NOTE: Do NOT commit encrypted_seed.txt (it's in .gitignore)
```

### STEP 5: Build Docker Container
```bash
# Install Python dependencies (for local testing)
pip3 install -r requirements.txt

# Build Docker image
docker-compose build --no-cache

# Start container
docker-compose up -d

# Verify running
docker-compose ps
```

### STEP 6: Test All 4 API Endpoints

**Test A: Health Check**
```bash
curl http://localhost:8080/health
# Expected: {"status":"ok"}
```

**Test B: Decrypt Seed**
```bash
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d "{\"encrypted_seed\": \"$(cat encrypted_seed.txt)\"}"
# Expected: {"status":"ok"}
```

**Test C: Generate 2FA Code**
```bash
curl http://localhost:8080/generate-2fa
# Expected: {"code":"XXXXXX","valid_for":XX}
```

**Test D: Verify TOTP Code**
```bash
# Get current code
CODE=$(curl -s http://localhost:8080/generate-2fa | grep -o '"code":"[^"]*' | cut -d'"' -f4)
echo "Testing with code: $CODE"

# Test valid code
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d "{\"code\": \"$CODE\"}"
# Expected: {"valid":true}

# Test invalid code
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"code": "000000"}'
# Expected: {"valid":false}
```

### STEP 7: Verify Cron Job (Wait 70+ Seconds)
```bash
echo "Waiting 70 seconds for cron execution..."
sleep 70

# Check cron output
docker exec pki-2fa-microservice cat /cron/last_code.txt
# Expected: Multiple lines with timestamps and codes
```

### STEP 8: Test Persistence (Container Restart)
```bash
# Stop container
docker-compose down

# Start again
docker-compose up -d

# Verify seed persists
docker exec pki-2fa-microservice cat /data/seed.txt

# Verify cron logs persist
docker exec pki-2fa-microservice cat /cron/last_code.txt
```

### STEP 9: Generate Commit Proof
```bash
# Ensure all changes committed
git add .
git commit -m "Complete PKI 2FA microservice implementation"
git push origin main

# Generate proof
python3 submission_proof.py

# Verify
cat submission_proof.txt
```

### STEP 10: Collect Submission Information
```bash
# Get commit hash
echo "=== COMMIT HASH ==="
git log -1 --format=%H

# Display all required info
echo ""
echo "=== STUDENT PUBLIC KEY ==="
cat student_public.pem

echo ""
echo "=== ENCRYPTED SEED ==="
cat encrypted_seed.txt

echo ""
echo "=== ENCRYPTED SIGNATURE ==="
grep "Encrypted Signature" submission_proof.txt

echo ""
echo "=== GITHUB REPO ==="
echo "https://github.com/KvPradeepthi/pki-2fa-microservice"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run: `pip3 install -r requirements.txt` |
| Docker build fails | Check Docker is running: `docker ps` |
| Port 8080 in use | Stop conflicting container: `docker ps`, then `docker stop <id>` |
| TOTP codes don't match | Verify timezone: `date` (should show UTC) |
| Cron not executing | Wait 70+ seconds, then check `/cron/last_code.txt` |
| Decryption fails | Ensure correct student private key is used |

## Expected Output Examples

```
✓ Encrypted seed saved to encrypted_seed.txt
{"status":"ok"}
{"code":"123456","valid_for":28}
{"valid":true}
2025-12-04 21:15:00 - 2FA Code: 123456
Commit Hash: abc123def456...
Encrypted Signature: MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQ...
```

## Files Generated

After all steps:
- ✅ `student_private.pem` - Your private key (committed to Git)
- ✅ `student_public.pem` - Your public key (committed to Git)
- ✅ `instructor_public.pem` - Instructor's public key (committed to Git)
- ✅ `encrypted_seed.txt` - Encrypted seed (NOT committed, in .gitignore)
- ✅ `submission_proof.txt` - Cryptographic proof (created locally)

## Ready to Submit!

Once all steps complete, you have:
1. Working PKI 2FA microservice
2. All application code committed to GitHub
3. Cryptographic proof of work
4. Complete submission data

Good luck! 🎓
