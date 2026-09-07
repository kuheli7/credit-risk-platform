# Use lightweight Python 3.11 base image
FROM python:3.11-slim

# Install system dependencies (curl needed for entrypoint DB download)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --no-cache-dir uv

WORKDIR /app

# Ensure src/ and backend/ are importable as top-level packages
ENV PYTHONPATH=/app

# Copy project manifest and lockfile
COPY pyproject.toml uv.lock ./

# Install dependencies into virtualenv without building this source tree as a package.
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source code
COPY . .

# Make the entrypoint executable
RUN chmod +x /app/docker-entrypoint.sh

# Ensure data directory exists (will be populated by entrypoint if needed)
RUN mkdir -p /app/data /app/models

# Expose FastAPI application port
EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Entrypoint handles optional DB download before app starts
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Run FastAPI platform
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
