FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV MARKDOWN_DIR=/app/markdown_data
ENV CHROMA_DB_DIR=/app/data/chroma
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

# Create necessary directories
RUN mkdir -p /app/data/chroma
RUN mkdir -p /app/markdown_data

# Expose API port
EXPOSE 8000

# Set up entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["api"]