import logging

from colorama import init, Fore
from confluent_kafka import Producer, KafkaException

from models.snapshot import SnapshotList

init(autoreset=True)

logger = logging.getLogger(__name__)


class KafkaTransporter:
    def __init__(self, kafka_brokers: str):
        """Initialize KafkaTransporter with broker addresses."""
        self.producer_conf = {
            'bootstrap.servers': kafka_brokers,
            'client.id': 'vvs-kafka-transporter',
            'acks': 'all',
            'retries': 5,
            'retry.backoff.ms': 500,
            'socket.timeout.ms': 10000,
        }
        self.producer = None

    def start(self):
        """Initialize the Kafka Producer."""
        try:
            self.producer = Producer(self.producer_conf)
            logger.info("Kafka Producer started successfully.")
        except KafkaException as e:
            logger.error(f"Failed to start Kafka Producer: {e}")

    def stop(self):
        """Flush and stop the Kafka Producer."""
        if self.producer:
            self.producer.flush(timeout=10)
            logger.info("Kafka Producer stopped.")
        else:
            logger.warning("Kafka Producer is not initialized.")

    def send_to_kafka(self, topic: str, key: str, message: str):
        """Send a message to Kafka."""
        if not self.producer:
            logger.error("Kafka Producer is not initialized.")
            return

        try:
            self.producer.produce(topic, key=key, value=message, callback=self.delivery_report)
            self.producer.poll(0)  # Trigger delivery callback
        except KafkaException as e:
            logger.error(f"Error while sending to Kafka: {e}")

    @staticmethod
    def delivery_report(err, msg):
        """Delivery callback to confirm message delivery."""
        if err is not None:
            logger.error(Fore.RED + f"Message delivery failed: {err}")
        else:
            logger.info(Fore.GREEN + f"Message delivered to {msg.topic()} [{msg.partition()}]")

    async def route_message(self, message):
        """Route messages from the QueueManager to Kafka."""
        # Example for sending SnapshotList:
        if isinstance(message, SnapshotList):
            key = "snapshot_key"  # You can customize the key based on message content
            self.send_to_kafka("snapshots", key, str(message))  # Convert message to string
        else:
            logger.warning(f"Unhandled message type: {type(message)}")
