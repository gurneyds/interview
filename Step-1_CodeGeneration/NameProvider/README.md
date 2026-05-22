# NameProvider Service

A Docker-based Python service that generates mock genealogy person records and publishes them to RabbitMQ. Designed as a development tool to proxy real genealogy systems for integration testing.

## 🎯 Purpose

The NameProvider service automatically maintains a minimum buffer of genealogy person records in a RabbitMQ queue, making test data continuously available to downstream systems without requiring production data access.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│  NameProvider Service (Python)                  │
│                                                  │
│  ┌──────────────┐      ┌──────────────┐        │
│  │   Monitor    │─────▶│  Generator   │        │
│  │   Thread     │      │   (Faker)    │        │
│  └──────┬───────┘      └──────┬───────┘        │
│         │                     │                 │
│         │ Check every 5s      │ Create Person   │
│         ▼                     ▼                 │
│  ┌──────────────────────────────┐              │
│  │   RabbitMQ Producer          │              │
│  │  (JSON, persistent msgs)     │              │
│  └──────────────┬───────────────┘              │
│                 │                               │
└─────────────────┼───────────────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │   RabbitMQ Queue   │
         │                    │
         │ Queue:             │
         │  genealogy-persons │
         │  (durable)         │
         └────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │ Your Application   │
         │  (Consumer)        │
         └────────────────────┘
```

### How It Works

1. **Monitor Thread**: Checks RabbitMQ queue depth every 5 seconds
2. **Threshold Detection**: When available messages < 10, triggers production
3. **Batch Production**: Generates needed records using Faker library
4. **RabbitMQ Publishing**: Sends JSON records with persistent delivery mode
5. **Auto-Recovery**: Handles RabbitMQ restarts and connection errors gracefully
6. **True Queue Semantics**: Messages are deleted after consumption (not pub/sub)

## 📦 Person Record Schema

Each generated person record contains:

**Required Fields (always present):**
- `firstName` - First name
- `lastName` - Last name  
- `recordId` - UUID v4 unique identifier
- `generatedAt` - ISO 8601 UTC timestamp

**Optional Fields (50% probability each):**
- `birthDate` - Date of birth (1800-1950 range)
- `deathDate` - Date of death (20-90 years after birth)
- `birthPlace` - City, State/Country
- `deathPlace` - City, State/Country
- `gender` - M (male), F (female), or U (unknown)

**Example Record:**
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
  "generatedAt": "2026-05-20T10:30:00.123456Z"
}
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- 2GB+ RAM available for RabbitMQ

### Start All Services

```bash
cd NameProvider
docker-compose up
```

This starts:
- RabbitMQ (ports 5672 for AMQP, 15672 for Management UI)
- NameProvider service

You should see logs indicating:
```
name-provider | Producer initialized for queue: genealogy-persons
name-provider | Monitor started: checking every 5s, maintaining minimum 10 messages
name-provider | Produced 10 records (was 0, now ~10)
```

### Consume Messages (Test Consumer)

In a new terminal:

```bash
# Consume 5 messages with compact output
python scripts/consume-messages-rabbitmq.py --count 5

# Consume 1 message with full JSON output
python scripts/consume-messages-rabbitmq.py --count 1 --verbose

# Continuous consumption (Ctrl+C to stop)
python scripts/consume-messages-rabbitmq.py --continuous
```

### RabbitMQ Management UI

Access the web interface at **http://localhost:15672**

- Username: `guest`
- Password: `guest`

View queue depth, message rates, and active consumers in real-time.

### Stop Services

```bash
docker-compose down
```

## ⚙️ Configuration

Configuration via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `RABBITMQ_HOST` | `localhost` | RabbitMQ server hostname |
| `RABBITMQ_PORT` | `5672` | RabbitMQ AMQP port |
| `RABBITMQ_USER` | `guest` | RabbitMQ username |
| `RABBITMQ_PASSWORD` | `guest` | RabbitMQ password |
| `QUEUE_NAME` | `genealogy-persons` | Queue name for person records |
| `MIN_QUEUE_SIZE` | `10` | Minimum messages to maintain |
| `BATCH_PRODUCTION_SIZE` | `5` | Records per production batch (unused currently) |
| `MONITOR_INTERVAL_SECONDS` | `5` | Seconds between queue checks |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

**To customize:** Create a `.env` file (copied from `.env.example`) and modify values.

## 🧪 Running Tests

```bash
# Install dependencies locally (optional, for IDE support)
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📚 RabbitMQ Concepts (For Beginners)

### What is RabbitMQ?

RabbitMQ is a message broker that implements AMQP (Advanced Message Queuing Protocol). Think of it as a true message queue where:
- Messages are deleted after consumption (queue semantics, not pub/sub)
- Multiple consumers can process messages in parallel (competing consumers)
- Messages are persistent and survive broker restarts

### Key Concepts

**Queues** 📬
- Named containers that hold messages
- Our queue: `genealogy-persons`
- Messages are deleted once acknowledged by a consumer
- Durable queues survive broker restarts

**Producers** 📤
- Applications that publish messages to queues
- NameProvider is a producer
- Sends JSON records with persistent delivery mode
- Automatic retries on connection failures

**Consumers** 📥
- Applications that read and process messages from queues
- Your downstream systems
- Messages are distributed round-robin among consumers
- Each message consumed by exactly one consumer

**Message Acknowledgment** ✅
- Consumer must acknowledge receipt of message
- Unacknowledged messages are redelivered if consumer crashes
- Prevents message loss during processing

### Why This Design?

✅ **True queue semantics**: Messages consumed = messages deleted  
✅ **Buffer prevents starvation**: 10-message minimum ensures consumers always have work  
✅ **Monitoring is simple**: Check queue depth directly  
✅ **Competing consumers**: Multiple consumers process messages in parallel  
✅ **Messages are durable**: RabbitMQ persists messages to disk

## 🔧 Troubleshooting

### Service won't start

**Check Docker resources:**
```bash
docker ps
docker logs genealogy-rabbitmq
docker logs genealogy-name-provider
```

**RabbitMQ takes 10-20 seconds to fully start.** Watch for:
```
rabbitmq | Server startup complete
```

### No messages appearing

**Check queue via Management UI:**
- Open http://localhost:15672
- Login with guest/guest
- Go to Queues tab
- Look for `genealogy-persons` queue
- Check "Ready" message count

**Or via command line:**
```bash
docker exec genealogy-rabbitmq rabbitmqctl list_queues
```

Expected output:
```
Listing queues for vhost / ...
genealogy-persons    10
```

### Producer connection errors

**Test RabbitMQ connectivity:**
```bash
# From host machine
nc -zv localhost 5672

# From inside Docker network
docker exec genealogy-name-provider nc -zv rabbitmq 5672
```

**Note:** 
- Host applications use `localhost:5672`
- Docker services use `rabbitmq:5672`

### Monitor not producing

**Enable debug logging:**

Edit `docker-compose.yml`:
```yaml
environment:
  LOG_LEVEL: DEBUG  # Change from INFO
```

Then restart:
```bash
docker-compose restart name-provider
docker logs -f genealogy-name-provider
```

## 🔍 RabbitMQ Management Commands

**List queues:**
```bash
docker exec genealogy-rabbitmq rabbitmqctl list_queues
```

**List consumers:**
```bash
docker exec genealogy-rabbitmq rabbitmqctl list_consumers
```

**Check queue details:**
```bash
docker exec genealogy-rabbitmq rabbitmqctl list_queues name messages consumers
```

**Purge queue (for testing):**
```bash
docker exec genealogy-rabbitmq rabbitmqctl purge_queue genealogy-persons
```

**View queue stats in browser:**
- Open http://localhost:15672
- Navigate to Queues → genealogy-persons
- View message rates, consumer connections, and memory usage

## 🏭 Production Considerations

This service is designed for **development and testing**. For production use, consider:

- [ ] Use Avro or Protobuf instead of JSON (schema evolution)
- [ ] Set up RabbitMQ cluster (3+ nodes for high availability)
- [ ] Add monitoring/metrics (Prometheus, Grafana)
- [ ] Implement circuit breakers for downstream failures
- [ ] Configure message TTL and dead letter queues
- [ ] Add authentication/encryption (TLS, user management)
- [ ] Set up federation or shovels for multi-datacenter
- [ ] Configure memory and disk limits
- [ ] Implement publisher confirms for guaranteed delivery

## 📊 RabbitMQ Best Practices Implemented

✅ **Queue naming**: Domain-entity pattern (`genealogy-persons`)  
✅ **Durable queues**: Queue survives broker restarts  
✅ **Persistent messages**: Messages survive broker restarts  
✅ **Serialization**: Structured JSON with schema validation  
✅ **Idempotency**: UUID recordId for deduplication tracking  
✅ **Metadata**: Timestamp for message lifecycle tracking  
✅ **Error handling**: Connection retry with graceful degradation  
✅ **Graceful shutdown**: Close connections cleanly  
✅ **Health checks**: Wait for RabbitMQ readiness before producing

## 📁 Project Structure

```
NameProvider/
├── docker-compose.yml       # Infrastructure definition
├── Dockerfile               # Python service container
├── requirements.txt         # Python dependencies
├── .env.example             # Configuration template
├── README.md                # This file
├── src/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── models.py            # Person data model (Pydantic)
│   ├── producer.py          # Kafka producer wrapper
│   ├── generator.py         # Mock data generator (Faker)
│   ├── monitor.py           # Queue monitoring thread
│   └── utils.py             # Logging and helpers
├── tests/
│   ├── test_models.py       # Model validation tests
│   ├── test_generator.py    # Data generation tests
│   └── test_producer.py     # Producer tests (mocked)
└── scripts/
    ├── wait-for-kafka.sh    # Health check script
    └── consume-messages.py  # Test consumer utility
```

## 🤝 Contributing

This is a development tool. To modify:

1. **Change schema**: Edit `src/models.py` and `src/generator.py`
2. **Adjust monitoring**: Modify `MIN_QUEUE_SIZE` or `MONITOR_INTERVAL_SECONDS`
3. **Add fields**: Update `PersonGenerator._generate_*` methods
4. **Change Kafka config**: Edit `src/producer.py` KafkaProducer settings

## 📝 License

Educational/Development Tool - Use freely for testing purposes.

## 🆘 Getting Help

- **Faker Docs**: https://faker.readthedocs.io/

---

**Happy Testing! 🚀** If you encounter issues, check the troubleshooting section or examine Docker logs.
