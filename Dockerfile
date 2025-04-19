FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY dca_alpaca_script.py .

# Create a default .env file (will be overwritten by mounted volume in production)
RUN echo "# Alpaca API Credentials\nALPACA_API_KEY=placeholder\nALPACA_API_SECRET=placeholder\nIS_PAPER=true" > .env

# Create directory for logs
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run the script
CMD ["python", "dca_alpaca_script.py"]