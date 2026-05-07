# Use same base as Flask for consistency
FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.12-slim as runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r celeryuser && useradd -r -g celeryuser celeryuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/celeryuser/.local

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p app/static/uploads celerybeat-schedule && \
    chown -R celeryuser:celeryuser /app

# Switch to non-root user
USER celeryuser

# Add local Python packages to PATH
ENV PATH=/home/celeryuser/.local/bin:$PATH

# Default command (overridden in docker-compose)
CMD ["celery", "-A", "app.extensions.celery", "worker", "--loglevel=info"]