# ==========================================
# Stage 1: Base Image with Python
# ==========================================
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    default-mysql-client \
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
    reports/logs

# ==========================================
# Stage 8: Expose Ports
# ==========================================
EXPOSE 3000
EXPOSE 5000

# ==========================================
# Stage 9: Set Environment Variables
# ==========================================
ENV PYTHONUNBUFFERED=1
ENV CI=true
ENV HEADLESS=true

# ==========================================
# Stage 10: Entry Point
# ==========================================
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

CMD ["/app/docker-entrypoint.sh"]
