
# Start from the official Python 3.12 slim image
FROM python:3.12-slim

# Set a working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install system dependencies and Python packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy application code into the container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create a non-root user for security and set permissions
RUN useradd -m myuser && chown -R myuser:myuser /app
USER myuser

# Expose the port if necessary for a web app (optional)
# EXPOSE 8080

# Start the bot with python
CMD ["python3", "bot.py"]
