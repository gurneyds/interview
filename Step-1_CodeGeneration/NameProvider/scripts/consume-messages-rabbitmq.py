#!/usr/bin/env python3
"""
Simple RabbitMQ consumer for testing the NameProvider service.

Usage:
    python scripts/consume-messages-rabbitmq.py --count 5
    python scripts/consume-messages-rabbitmq.py --continuous
"""
import argparse
import json
import sys
import pika


def consume_messages(host: str, port: int, user: str, password: str, queue_name: str,
                    count: int = None, verbose: bool = False):
    """
    Consume messages from the RabbitMQ queue.

    Args:
        host: RabbitMQ server hostname
        port: RabbitMQ server port
        user: RabbitMQ username
        password: RabbitMQ password
        queue_name: Queue name to consume from
        count: Number of messages to consume (None for continuous)
        verbose: Print full message content
    """
    try:
        # Create connection
        credentials = pika.PlainCredentials(user, password)
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials
        )

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Declare queue (ensure it exists)
        channel.queue_declare(queue=queue_name, durable=True)

        print(f"Connected to RabbitMQ at {host}:{port}")
        print(f"Consuming from queue: {queue_name}")
        print(f"Mode: {'Continuous' if count is None else f'{count} messages'}")
        print("-" * 80)

        consumed = 0

        def callback(ch, method, properties, body):
            nonlocal consumed
            consumed += 1

            try:
                person = json.loads(body)

                if verbose:
                    print(f"\nMessage {consumed}:")
                    print(f"  Delivery Tag: {method.delivery_tag}")
                    print(f"  Person Data:")
                    print(json.dumps(person, indent=4))
                else:
                    # Compact format
                    name = f"{person.get('firstName')} {person.get('lastName')}"
                    birth = person.get('birthDate', 'N/A')
                    death = person.get('deathDate', 'N/A')
                    gender = person.get('gender', 'N/A')
                    print(f"{consumed}. {name} | Birth: {birth} | Death: {death} | Gender: {gender}")

                # Acknowledge message (this removes it from queue)
                ch.basic_ack(delivery_tag=method.delivery_tag)

                # Stop if we've consumed enough
                if count is not None and consumed >= count:
                    ch.stop_consuming()

            except json.JSONDecodeError as e:
                print(f"Error decoding message: {e}", file=sys.stderr)
                ch.basic_ack(delivery_tag=method.delivery_tag)  # Still acknowledge to remove bad message

        # Start consuming
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            channel.stop_consuming()

        print("-" * 80)
        print(f"Total messages consumed: {consumed}")
        connection.close()

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Connection error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Consume genealogy person records from RabbitMQ"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="RabbitMQ hostname (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5672,
        help="RabbitMQ port (default: 5672)"
    )
    parser.add_argument(
        "--user",
        default="guest",
        help="RabbitMQ username (default: guest)"
    )
    parser.add_argument(
        "--password",
        default="guest",
        help="RabbitMQ password (default: guest)"
    )
    parser.add_argument(
        "--queue",
        default="genealogy-persons",
        help="Queue name (default: genealogy-persons)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Number of messages to consume (default: continuous)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print full message content"
    )

    args = parser.parse_args()

    consume_messages(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        queue_name=args.queue,
        count=args.count,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()
