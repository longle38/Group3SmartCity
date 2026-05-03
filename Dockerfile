# =============================================================================
# ENPM818T -- GP3 Scenario 1 (Traffic)
# Dockerfile starter for the Python application
# -----------------------------------------------------------------------------
# Layer order is chosen for cache efficiency:
#   1. Base image + OS packages (rarely change)
#   2. requirements.txt + pip install (changes sometimes)
#   3. Application source (changes constantly)
# =============================================================================

FROM python:3.12-slim AS app

# Keep Python output unbuffered so container logs show up immediately.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System-level build deps for psycopg2 / cryptography wheels.
# If you use psycopg2-binary you can remove libpq-dev + build-essential,
# but keeping them makes the image work with either wheel.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps FIRST for better layer caching.
COPY requirements.txt ./
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Copy the rest of the project.
COPY . .

# Default command: launch the menu-driven CLI.
# Adjust the module path to wherever your main() lives.
CMD ["python", "-m", "cli.main"]