FROM --platform=linux/amd64 python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies with uv
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy application files
COPY bot.py .

# Run the bot
CMD ["python", "bot.py"] 