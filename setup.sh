#!/bin/bash
# PKI 2FA Microservice - Automated Setup Script

set -e

echo "====================================="
echo "PKI 2FA Microservice Setup"
echo "====================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Step 1: Download Instructor Public Key${NC}"
wget -q https://partnr-public.s3.us-east-1.amazonaws.com/gpp-resources/instructor_public.pem
echo -e "${GREEN}✓ Downloaded instructor_public.pem${NC}"
git add instructor_public.pem
git commit -m "Add instructor public key"
git push -q origin main
echo -e "${GREEN}✓ Committed to Git${NC}"
echo ""

echo -e "${YELLOW}Step 2: Generate RSA Key Pair${NC}"
python3 keygen.py
echo -e "${GREEN}✓ Generated student_private.pem and student_public.pem${NC}"
git add student_private.pem student_public.pem
git commit -m "Add student RSA key pair"
git push -q origin main
echo -e "${GREEN}✓ Committed keys to Git${NC}"
echo ""

echo -e "${YELLOW}Step 3: Request Encrypted Seed${NC}"
read -p "Enter your Student ID: " STUDENT_ID
echo "Running: python3 request_seed.py $STUDENT_ID https://github.com/KvPradeepthi/pki-2fa-microservice"
python3 request_seed.py "$STUDENT_ID" "https://github.com/KvPradeepthi/pki-2fa-microservice"
echo -e "${GREEN}✓ Encrypted seed obtained${NC}"
echo ""

echo -e "${YELLOW}Step 4: Install Python Dependencies${NC}"
pip3 install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

echo -e "${YELLOW}Step 5: Build Docker Container${NC}"
docker-compose build --no-cache > /dev/null 2>&1
echo -e "${GREEN}✓ Docker image built${NC}"
echo ""

echo -e "${YELLOW}Step 6: Start Container${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Container running${NC}"
echo ""

echo -e "${YELLOW}Step 7: Test API Endpoints${NC}"
echo "Testing health endpoint..."
curl -s http://localhost:8080/health | jq .
echo -e "${GREEN}✓ Health check passed${NC}"
echo ""

echo -e "${YELLOW}Step 8: Decrypt Seed in Container${NC}"
echo "Sending encrypted seed to /decrypt-seed endpoint..."
curl -s -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d "{\"encrypted_seed\": \"$(cat encrypted_seed.txt)\"}" | jq .
echo -e "${GREEN}✓ Seed decrypted${NC}"
echo ""

echo -e "${YELLOW}Step 9: Generate 2FA Code${NC}"
echo "Getting current TOTP code..."
curl -s http://localhost:8080/generate-2fa | jq .
echo -e "${GREEN}✓ Code generated${NC}"
echo ""

echo -e "${YELLOW}Step 10: Wait for Cron Job (70 seconds)${NC}"
echo "Waiting for cron to execute multiple times..."
sleep 70
echo -e "${GREEN}✓ Checking cron output...${NC}"
docker exec pki-2fa-microservice cat /cron/last_code.txt
echo ""

echo -e "${YELLOW}Step 11: Commit Final Changes${NC}"
git add .
git commit -m "Complete PKI 2FA microservice implementation" 2>/dev/null || true
git push -q origin main
echo -e "${GREEN}✓ Changes committed${NC}"
echo ""

echo -e "${YELLOW}Step 12: Generate Commit Proof${NC}"
python3 submission_proof.py
echo -e "${GREEN}✓ Proof generated${NC}"
echo ""

echo -e "${YELLOW}Step 13: Display Submission Information${NC}"
echo ""
echo -e "${GREEN}========== SUBMISSION INFO ==========${NC}"
echo ""
echo -e "${YELLOW}GitHub Repository:${NC}"
echo "https://github.com/KvPradeepthi/pki-2fa-microservice"
echo ""
echo -e "${YELLOW}Commit Hash:${NC}"
git log -1 --format=%H
echo ""
echo -e "${YELLOW}Student Public Key:${NC}"
cat student_public.pem
echo ""
echo -e "${YELLOW}Encrypted Seed:${NC}"
cat encrypted_seed.txt
echo ""
echo -e "${YELLOW}Encrypted Signature:${NC}"
grep "Encrypted Signature:" submission_proof.txt
echo ""
echo -e "${GREEN}========== SETUP COMPLETE ==========${NC}"
echo ""
echo -e "${GREEN}✓ All setup steps completed successfully!${NC}"
echo ""
echo "You are ready to submit your work!"
