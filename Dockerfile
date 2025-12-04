# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
ENV TZ=UTC
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Configure timezone
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime && echo UTC > /etc/timezone

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application files
COPY app/ /app/app/
COPY scripts/ /app/scripts/
COPY cron/ /app/cron/
COPY *.pem /app/
COPY *.py /app/

# Setup cron
RUN chmod 0644 /app/cron/2fa-cron && crontab /app/cron/2fa-cron

# Create volume mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

EXPOSE 8080

# Start cron and API server
CMD cron && python3 /app/app/main.py
