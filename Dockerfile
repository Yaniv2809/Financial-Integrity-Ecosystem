# ==========================================
# Stage 1: Base Image with Python
# ==========================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# Stage 2: Install Node.js (for JSON Server)
# ==========================================
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# Stage 3: Copy Project Files
# ==========================================
COPY requirements.txt .
COPY . .

# ==========================================
# Stage 4: Install Python Dependencies
# ==========================================
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 5: Install Playwright Browsers
# ==========================================
RUN playwright install chromium \
    && playwright install-deps

# ==========================================
# Stage 6: Install JSON Server Dependencies
# ==========================================
WORKDIR /app/json-server
RUN npm install
WORKDIR /app

# ==========================================
# Stage 7: Create Directories for Reports
# ==========================================
RUN mkdir -p reports/screenshots \
    reports/traces \
    reports/videos \
    logs

# ==========================================
# Stage 8: Expose Port (for JSON Server)
# ==========================================
EXPOSE 3000

# ==========================================
# Stage 9: Set Environment Variables
# ==========================================
ENV PYTHONUNBUFFERED=1
ENV PYTEST_ADDOPTS="--html=reports/report.html --self-contained-html"

# ==========================================
# Stage 10: Entry Point
# ==========================================
# Start JSON Server in background and run tests
CMD ["sh", "-c", "cd json-server && npm start & sleep 5 && cd .. && pytest"]


