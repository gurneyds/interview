# External Consumer Example

This demonstrates how an external Docker container can consume messages from the NameProvider's RabbitMQ queue.

## How It Works

1. **Shares RabbitMQ's network namespace** (simple, no custom networks)
2. Connects to RabbitMQ using service name (`rabbitmq`)
3. Consumes messages from `genealogy-persons` queue
4. Processes each person record
5. Acknowledges messages (removes from queue)

## Quick Start

### 1. Start NameProvider (if not running)

```bash
cd /Users/gurneyds/dev/interview/NameProvider
docker-compose up -d
```

### 2. Start External Consumer

```bash
cd example-external-consumer
docker-compose up --build
```

### What You'll See

```
External Consumer Starting...
Connecting to RabbitMQ at rabbitmq:5672
Queue: genealogy-persons
============================================================
Connected! Waiting for messages...

Processing: John Smith
  Record ID: a1b2c3d4-...
  Birth: 1842-03-15
  Gender: M
------------------------------------------------------------
Processing: Jane Doe
  Record ID: e5f6g7h8-...
  Birth: Unknown
  Gender: F
------------------------------------------------------------
...
```

### Stop the Consumer

```bash
docker-compose down
```

## Key Features

✅ **Simple setup** - No custom network configuration needed  
✅ **Runs in separate container** from NameProvider  
✅ **Auto-connects** to existing RabbitMQ instance  
✅ **Processes one message at a time** (`prefetch_count=1`)  
✅ **Graceful error handling** (requeues on failure)  
✅ **Auto-restart** on crash  

## How the Connection Works

The external consumer uses `network_mode: "container:genealogy-rabbitmq"` which means:
- It shares the RabbitMQ container's network namespace
- Both containers see each other as `localhost`
- No need to create or manage custom Docker networks
- Simplest possible configuration

## Testing Auto-Replenishment

1. Start NameProvider (maintains 10 messages)
2. Start this external consumer
3. Watch consumer process messages
4. Check NameProvider logs - it will auto-produce more as queue drains

```bash
# In another terminal
docker logs -f genealogy-name-provider | grep Produced
```

Expected output:
```
Produced 10 records (was 0, now ~10)
Produced 8 records (was 2, now ~10)  # Auto-replenished!
Produced 7 records (was 3, now ~10)
```
