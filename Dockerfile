# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app
W
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install sympy (main dependency identified from code)
RUN pip install --no-cache-dir sympy

# Copy the entire project
COPY . .

# Set Python path to include the pycr directory
ENV PYTHONPATH="${PYTHONPATH}:/app/pycr"

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port (adjust if your application uses a specific port)
EXPOSE 8000

# Default command - adjust based on your application's entry point
CMD ["python", "-c", "from pycr.crmake import *; print('Chains of Recurrences engine ready!')"]