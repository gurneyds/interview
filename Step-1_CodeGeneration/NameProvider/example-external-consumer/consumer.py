#!/usr/bin/env python3
"""
Example external consumer that processes genealogy person records.
"""
import os
import json
import time
import pika

def process_person(person_data):
    """
    Process a person record (your business logic here).
    """
    name = f"{person_data.get('firstName')} {person_data.get('lastName')}"
    print(f"Processing: {name}")
    print(f"  Record ID: {person_data.get('recordId')}")
    print(f"  Birth: {person_data.get('birthDate', 'Unknown')}")
    print(f"  Gender: {person_data.get('gender', 'Unknown')}")
    print("-" * 60)

    # Simulate some processing work
    time.sleep(0.5)

def main():
    # Configuration from environment
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
    rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
    rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')
    queue_name = os.getenv('QUEUE_NAME', 'genealogy-persons')

    print(f"External Consumer Starting...")
    print(f"Connecting to RabbitMQ at {rabbitmq_host}:{rabbitmq_port}")
    print(f"Queue: {queue_name}")
    print("=" * 60)

    # Connect to RabbitMQ
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        credentials=credentials,
        heartbeat=600
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Ensure queue exists
    channel.queue_declare(queue=queue_name, durable=True)

    print(f"Connected! Waiting for messages...\n")

    def callback(ch, method, properties, body):
        """Handle incoming messages."""
        try:
            person_data = json.loads(body)
            process_person(person_data)

            # Acknowledge message (removes from queue)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"Error processing message: {e}")
            # Reject and requeue on error
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    # Set QoS - only process 1 message at a time
    channel.basic_qos(prefetch_count=1)

    # Start consuming
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=False
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == "__main__":
    main()
