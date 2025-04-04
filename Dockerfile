# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Disable Python output buffering - important for logs
ENV PYTHONUNBUFFERED=1

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files to the container
COPY . .

# Environment variables (these can be overridden when running the container)
ENV BOT_TOKEN=""
ENV ADMINS_IDS=""
ENV CHANNEL_TAG=""

# Run the bot
CMD ["python", "main.py"]
