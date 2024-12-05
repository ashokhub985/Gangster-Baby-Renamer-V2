
# Stage 1: Build stage
FROM python:3.12-slim AS builder

# Set a working directory in the container
WORKDIR /app

# Copy requirements file into the container
COPY requirements.txt /app/

# Install system dependencies needed for building
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Stage 2: Final image
FROM python:3.12-slim

# Set a working directory in the container
WORKDIR /app

# Copy only necessary files from the builder stage
COPY --from=builder /app /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN useradd -m myuser && chown -R myuser:myuser /app
USER myuser

# Expose port if necessary (optional)
# EXPOSE 8080

# Start the bot with python
CMD ["python3", "bot.py"]
