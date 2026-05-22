"""
Tests for PersonProducer.

Note: These tests mock the KafkaProducer to avoid requiring a real Kafka instance.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.producer import PersonProducer
from src.models import Person


@patch('src.producer.KafkaProducer')
def test_producer_initialization(mock_kafka_producer):
    """Test that producer initializes with correct configuration."""
    producer = PersonProducer(
        bootstrap_servers="localhost:9092",
        topic="test-topic"
    )

    # Verify KafkaProducer was called with expected config
    mock_kafka_producer.assert_called_once()
    call_kwargs = mock_kafka_producer.call_args[1]

    assert call_kwargs['bootstrap_servers'] == "localhost:9092"
    assert call_kwargs['acks'] == 1
    assert call_kwargs['compression_type'] == 'gzip'
    assert call_kwargs['retries'] == 3


@patch('src.producer.KafkaProducer')
def test_producer_send_success(mock_kafka_producer):
    """Test successful message send."""
    # Setup mock
    mock_instance = Mock()
    mock_future = Mock()
    mock_metadata = Mock()
    mock_metadata.partition = 0
    mock_metadata.offset = 42
    mock_future.get.return_value = mock_metadata
    mock_instance.send.return_value = mock_future
    mock_kafka_producer.return_value = mock_instance

    # Create producer and send message
    producer = PersonProducer(
        bootstrap_servers="localhost:9092",
        topic="test-topic"
    )

    person = Person(firstName="John", lastName="Smith")
    result = producer.send(person)

    # Verify
    assert result is True
    mock_instance.send.assert_called_once()
    assert mock_instance.send.call_args[0][0] == "test-topic"


@patch('src.producer.KafkaProducer')
def test_producer_flush(mock_kafka_producer):
    """Test producer flush."""
    mock_instance = Mock()
    mock_kafka_producer.return_value = mock_instance

    producer = PersonProducer(
        bootstrap_servers="localhost:9092",
        topic="test-topic"
    )

    producer.flush()

    mock_instance.flush.assert_called_once()


@patch('src.producer.KafkaProducer')
def test_producer_close(mock_kafka_producer):
    """Test producer close."""
    mock_instance = Mock()
    mock_kafka_producer.return_value = mock_instance

    producer = PersonProducer(
        bootstrap_servers="localhost:9092",
        topic="test-topic"
    )

    producer.close()

    mock_instance.flush.assert_called_once()
    mock_instance.close.assert_called_once()
