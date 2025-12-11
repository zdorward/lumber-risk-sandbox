FROM python:3.11-slim

WORKDIR /app

# Saner Python defaults
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps (for builds, matplotlib, etc. adjust as needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Default command: run the FastAPI backend
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]