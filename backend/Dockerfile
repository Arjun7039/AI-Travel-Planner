FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for python packages and postgres
RUN apt-get update && apt-get install -y gcc g++ libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements from the backend folder context
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend source code into /app/backend
COPY . /app/backend

# Ensure python path is correct so 'backend' is a top-level module
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
