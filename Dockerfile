# Use Ubuntu 20.04 as the base image
FROM ubuntu:20.04

# Set non-interactive mode to prevent tzdata or other packages from prompting during installation
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory inside the container
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a directory for background images
RUN mkdir -p static/background

# Expose port 81 for the Flask application
EXPOSE 81

# Command to run the application
CMD ["python3", "app.py"]
