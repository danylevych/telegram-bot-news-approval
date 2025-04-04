# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files to the container
COPY main.py .
COPY configs/ ./configs/
COPY handlers/ ./handlers/
COPY logger/ ./logger/
COPY models/ ./models/
COPY utils/ ./utils/


# Run the bot
CMD ["python", "main.py"]
