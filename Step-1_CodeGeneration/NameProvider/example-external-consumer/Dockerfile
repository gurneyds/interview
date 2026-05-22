FROM python:3.11-slim

WORKDIR /app

# Install pika
RUN pip install --no-cache-dir pika

# Copy consumer script
COPY consumer.py .

CMD ["python", "-u", "consumer.py"]
