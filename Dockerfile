# ── Stage 1: base image ───────────────────────────────────────────────────────
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies first (layer-cache friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start the FastAPI web server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
