# PKI 2FA Microservice

Enterprise-grade authentication microservice with RSA 4096-bit encryption and TOTP 2FA.

## Features

- RSA 4096-bit key pair generation with public exponent 65537
- RSA/OAEP-SHA256 decryption of encrypted seeds
- TOTP code generation (SHA-1, 30s period, 6-digit)
- TOTP verification with ±30 second tolerance
- REST API endpoints with proper HTTP status codes
- Docker multi-stage build with cron scheduling
- Persistent storage for seed and cron logs
- UTC timezone enforcement

## Setup

```bash
git clone https://github.com/KvPradeepthi/pki-2fa-microservice
cd pki-2fa-microservice
mkdir -p app scripts cron

python3 keygen.py
python3 request_seed.py YOUR_STUDENT_ID https://github.com/KvPradeepthi/pki-2fa-microservice

docker-compose build
docker-compose up -d
```

## API Endpoints

- `POST /decrypt-seed` - Decrypt encrypted seed
- `GET /generate-2fa` - Generate current TOTP code
- `POST /verify-2fa` - Verify TOTP code
- `GET /health` - Health check

## Testing

```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/decrypt-seed -H "Content-Type: application/json" -d "{\"encrypted_seed\": \"$(cat encrypted_seed.txt)\"}"
curl http://localhost:8080/generate-2fa
```

## Security

- RSA/OAEP with MGF1(SHA-256)
- RSA-PSS signatures with max salt length
- Private keys stored securely in container
- Input validation on all endpoints
- Proper error handling
- UTC timezone for consistency

## Author

KvPradeepthi - Global Placement Program
