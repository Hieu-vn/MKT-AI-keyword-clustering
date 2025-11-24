# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system build dependencies for HDBSCAN and others
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy the dependency files
COPY pyproject.toml poetry.lock ./

# Install NumPy and hdbscan first via pip to avoid poetry build issues
RUN pip install numpy Cython
RUN pip install hdbscan

# Configure poetry to use system site packages
RUN poetry config virtualenvs.options.system-site-packages true

# Install project dependencies
# --no-root: Don't install the project itself, just the dependencies
# --without dev: Don't install development dependencies
# Regenerate lock file to ensure consistency
RUN poetry lock
RUN poetry install --no-root --without dev

# Copy the application source code
COPY keyword_cluster_app/ ./keyword_cluster_app/

# Add the app directory to the PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"
