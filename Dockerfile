# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /usr/src/app

# Clear out the local repository of retrieved package files
RUN rm -rf /var/lib/apt/lists/*

# Install system dependencies with a retry loop
RUN set -ex; \
    for i in 1 2 3; do \
        apt-get update && apt-get -y install netcat gcc && apt-get clean && break || sleep 15; \
    done

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the app
CMD ["python", "app.py"]
