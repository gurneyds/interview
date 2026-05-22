#!/bin/bash
#
# Wait for Kafka to be ready before starting the application.
# This script is called from the Dockerfile CMD.
#

set -e

KAFKA_HOST="${KAFKA_BOOTSTRAP_SERVERS:-kafka:29092}"
MAX_RETRIES=30
RETRY_DELAY=2

echo "Waiting for Kafka at ${KAFKA_HOST}..."

for i in $(seq 1 $MAX_RETRIES); do
    if nc -z ${KAFKA_HOST%%:*} ${KAFKA_HOST##*:}; then
        echo "Kafka is ready!"
        exec "$@"
    fi
    echo "Kafka not ready, waiting... (${i}/${MAX_RETRIES})"
    sleep $RETRY_DELAY
done

echo "ERROR: Kafka not available after ${MAX_RETRIES} attempts"
exit 1
