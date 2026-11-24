FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p data logs output static templates

# Expose port
EXPOSE 8080

# Run the admin panel
CMD ["python", "-c", "from src.admin_panel import run_admin_panel; run_admin_panel(host='0.0.0.0', port=8080)"]