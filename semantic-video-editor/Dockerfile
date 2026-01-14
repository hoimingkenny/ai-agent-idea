# Dockerfile for Semantic Video Editor Agent
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for audio/video processing and ZMQ
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libzmq3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose ZeroMQ ports
EXPOSE 5555 5556

CMD ["python", "src/agent/controller.py"]
