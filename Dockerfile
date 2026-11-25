# Use an official lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependency list first for faster Docker caching
COPY requirements.txt .

# Install Python dependencies without keeping pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files into the container
COPY . .

# Document that the Flask app listens on port 5001
EXPOSE 5001

# Start the Flask application when the container runs
CMD ["python", "app.py"]
