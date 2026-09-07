# Use lightweight Python 3.11 base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy project manifest and lockfile
COPY pyproject.toml uv.lock ./

# Install dependencies into virtualenv without building this source tree as a package.
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source code
COPY . .

# Expose FastAPI application port
EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Run FastAPI platform
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
