FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY . .

# Set environment variable for port
ENV PORT=8501

# Expose the port
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "talk.py", "--server.port", "$PORT", "--server.address", "0.0.0.0"]
