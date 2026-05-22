# Consumer Quick Start

## Connection Details

| Parameter | Value |
|-----------|-------|
| **Host** | `localhost` |
| **Port** | `5672` |
| **Username** | `guest` |
| **Password** | `guest` |
| **Queue Name** | `genealogy-persons` |
| **Protocol** | AMQP 0-9-1 |

## Message Format

Messages are JSON with the following structure:

```json
{
  "firstName": "John",
  "lastName": "Smith",
  "birthDate": "1842-03-15",
  "deathDate": "1923-11-02",
  "birthPlace": "Boston, MA",
  "deathPlace": "Seattle, WA",
  "gender": "M",
  "recordId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "generatedAt": "2026-05-20T10:30:00.000000Z"
}
```

**Required fields:** `firstName`, `lastName`, `recordId`, `generatedAt`  
**Optional fields:** `birthDate`, `deathDate`, `birthPlace`, `deathPlace`, `gender`

## Minimal Python Example

```python
import pika
import json

# Connect
credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', 5672, credentials=credentials)
)
channel = connection.channel()

# Consume
def callback(ch, method, properties, body):
    person = json.loads(body)
    print(f"{person['firstName']} {person['lastName']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume('genealogy-persons', callback, auto_ack=False)
channel.start_consuming()
```

## Client Libraries

- **Python:** `pip install pika`
- **Java:** `com.rabbitmq:amqp-client`
- **Node.js:** `npm install amqplib`
- **Go:** `github.com/rabbitmq/amqp091-go`
- **.NET:** `RabbitMQ.Client`

## Management UI

**URL:** http://localhost:15672  
**Credentials:** guest / guest

Monitor queue depth, message rates, and consumer connections.

## Important Notes

- **Messages are deleted after acknowledgment** (queue semantics, not pub/sub)
- Queue is automatically maintained with minimum 10 messages
- Use manual acknowledgment (`auto_ack=False`) to prevent message loss
- Queue is durable (`durable=True`)
