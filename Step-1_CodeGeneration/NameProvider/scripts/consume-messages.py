#!/usr/bin/env python3
"""
Simple Kafka consumer for testing the NameProvider service.

Usage:
    python scripts/consume-messages.py --count 5 --verbose
    python scripts/consume-messages.py --continuous
"""
import argparse
import json
import sys
from kafka import KafkaConsumer
from kafka.errors import KafkaError


def consume_messages(bootstrap_servers: str, topic: str, count: int = None, verbose: bool = False,
                    from_beginning: bool = False, group_id: str = None):
    """
    Consume messages from the Kafka topic.

    Args:
        bootstrap_servers: Kafka broker address
        topic: Topic name to consume from
        count: Number of messages to consume (None for continuous)
        verbose: Print full message content
        from_beginning: If True, read from start (ignores saved offset)
        group_id: Consumer group ID (None creates unique group each run)
    """
    try:
        # If from_beginning or no group_id, create unique consumer group to read from start
        if from_beginning or group_id is None:
            import uuid
            group_id = f'test-consumer-{uuid.uuid4()}'
            offset_reset = 'earliest'
        else:
            offset_reset = 'latest'  # Continue from where group left off

        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset=offset_reset,
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=10000  # Exit after 10s of no messages
        )

        print(f"Connected to Kafka at {bootstrap_servers}")
        print(f"Consuming from topic: {topic}")
        print(f"Consumer group: {group_id}")
        print(f"Mode: {'Continuous' if count is None else f'{count} messages'}")
        print(f"Starting from: {'beginning' if from_beginning else 'last offset'}")
        print("-" * 80)

        consumed = 0
        for message in consumer:
            consumed += 1
            person = message.value

            if verbose:
                print(f"\nMessage {consumed}:")
                print(f"  Partition: {message.partition}")
                print(f"  Offset: {message.offset}")
                print(f"  Person Data:")
                print(json.dumps(person, indent=4))
            else:
                # Compact format
                name = f"{person.get('firstName')} {person.get('lastName')}"
                birth = person.get('birthDate', 'N/A')
                death = person.get('deathDate', 'N/A')
                gender = person.get('gender', 'N/A')
                print(f"{consumed}. {name} | Birth: {birth} | Death: {death} | Gender: {gender}")

            if count is not None and consumed >= count:
                break

        print("-" * 80)
        if consumed == 0:
            print("No messages consumed. Possible reasons:")
            print("  - Topic is empty")
            print("  - Consumer group already read all messages (try --from-beginning)")
            print("  - Timeout waiting for new messages")
        else:
            print(f"Total messages consumed: {consumed}")
        consumer.close()

    except KafkaError as e:
        print(f"Kafka error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        consumer.close()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Consume genealogy person records from Kafka"
    )
    parser.add_argument(
        "--bootstrap-servers",
        default="localhost:9092",
        help="Kafka bootstrap servers (default: localhost:9092)"
    )
    parser.add_argument(
        "--topic",
        default="genealogy-persons",
        help="Kafka topic name (default: genealogy-persons)"
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
    parser.add_argument(
        "--from-beginning",
        action="store_true",
        help="Read from start of topic (ignores saved offset)"
    )
    parser.add_argument(
        "--group-id",
        default=None,
        help="Consumer group ID (default: unique group each run)"
    )

    args = parser.parse_args()

    consume_messages(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic,
        count=args.count,
        verbose=args.verbose,
        from_beginning=args.from_beginning,
        group_id=args.group_id
    )


if __name__ == "__main__":
    main()
