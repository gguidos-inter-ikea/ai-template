# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file first to leverage Docker cache for dependency installation
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# Make the entrypoint script executable
RUN chmod +x entrypoint.py

# Expose the port that the app runs on
EXPOSE 8000

# Define environment variable (optional, as they're set in docker-compose)
ENV PYTHONPATH=/app

# Command to run the application using our custom entrypoint
CMD ["python", "entrypoint.py"]
