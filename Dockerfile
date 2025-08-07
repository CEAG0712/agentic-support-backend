# Use official Python image
FROM python:3.12

# Set working directory
WORKDIR /app

# Copy requirements first for cache optimization
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose default FastAPI port
EXPOSE 8000

# Run FastAPI app via uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

