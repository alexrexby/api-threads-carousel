# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    software-properties-common \
    git \
    pkg-config \
    # Font and image processing dependencies
    fontconfig \
    fonts-dejavu-core \
    fonts-noto-color-emoji \
    fonts-liberation \
    fonts-noto-core \
    fonts-noto-ui-core \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    zlib1g-dev \
    # Additional tools for font management
    unzip \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Update font cache
RUN fc-cache -fv

# Create fonts directories
RUN mkdir -p /app/fonts /app/fonts/cache /app/fonts/google

# Download some popular Google Fonts for offline use (optional)
# This ensures the service works even without internet access for these fonts
RUN cd /tmp && \
    # Download Inter font
    wget -q "https://github.com/rsms/inter/releases/download/v3.19/Inter-3.19.zip" -O inter.zip && \
    unzip -q inter.zip "Inter Desktop/*" && \
    cp "Inter Desktop/"*.ttf /app/fonts/ && \
    # Download Roboto font
    wget -q "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf" -O /app/fonts/Roboto-400.ttf && \
    wget -q "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf" -O /app/fonts/Roboto-700.ttf && \
    # Download Open Sans
    wget -q "https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Regular.ttf" -O /app/fonts/OpenSans-400.ttf && \
    wget -q "https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Bold.ttf" -O /app/fonts/OpenSans-700.ttf && \
    # Clean up
    rm -rf /tmp/* && \
    # Update font cache again
    fc-cache -fv

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Copy application code
COPY --chown=app:app . .

# Create necessary directories with proper permissions
RUN mkdir -p logs temp fonts/cache

# Set proper permissions for fonts directory
USER root
RUN chown -R app:app /app/fonts && chmod -R 755 /app/fonts
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Set default environment with Google Fonts support
ENV FLASK_ENV=production \
    FLASK_DEBUG=False \
    API_HOST=0.0.0.0 \
    API_PORT=5000 \
    DEFAULT_FONT_FAMILY=Inter \
    DEFAULT_FONT_WEIGHT=400 \
    TITLE_FONT_WEIGHT=600 \
    FONT_PATH=/app/fonts/ \
    FONTS_CACHE_DIR=/app/fonts/cache/

# Run the application
CMD ["python", "app.py"]
