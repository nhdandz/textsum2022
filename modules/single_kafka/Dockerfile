FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including mupdf for PyMuPDF and OpenSSL for aspose-words
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    mupdf \
    mupdf-tools \
    libmupdf-dev \
    libssl-dev \
    libssl3 \
    openssl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install OpenSSL 1.1 for aspose-words .NET Core runtime compatibility
# aspose-words uses .NET Core which requires libssl.so.1.1 and libcrypto.so.1.1
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb && \
    dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb && \
    rm libssl1.1_1.1.1f-1ubuntu2_amd64.deb

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 9980

# Default command - Chạy với Gunicorn cho production
# Nếu muốn dùng Flask development server, thay bằng: CMD ["python", "app_process.py"]
CMD ["gunicorn", "--config", "gunicorn_config.py", "app_process:app"]
