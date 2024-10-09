import logging
import json
import time
from colorama import init, Fore
from confluent_kafka import Producer, KafkaException

init(autoreset=True)

logger = logging.getLogger(__name__)

class KafkaTransporter:
    def __init__(self, kafka_brokers: str):
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
        try:
            self.producer = Producer(self.producer_conf)
            logger.info("Kafka Producer started successfully.")
        except KafkaException as e:
            logger.error(f"Failed to start Kafka Producer: {e}")

    def stop(self):
        if self.producer:
            self.producer.flush(timeout=10)
            logger.info("Kafka Producer stopped.")
        else:
            logger.warning("Kafka Producer is not initialized.")

    def send_to_kafka(self, topic: str, key: str, message: str):
        if not self.producer:
            logger.error("Kafka Producer is not initialized.")
            return

        try:
            self.producer.produce(topic, key=key, value=message.encode('utf-8'), callback=self.delivery_report)
            self.producer.poll(0)
        except KafkaException as e:
            logger.error(f"Error while sending to Kafka: {e}")

    @staticmethod
    def delivery_report(err, msg):
        if err is not None:
            logger.error(Fore.RED + f"Message delivery failed: {err}")
        else:
            logger.info(Fore.GREEN + f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def serialize_snapshot_list(self, snapshots, key, timestamp, name):
        snapshot_list = {
            'key': key,
            'time': timestamp,
            'name': name,
            'snapshots': snapshots
        }
        return json.dumps(snapshot_list)

    async def route_message(self, message):
        if not isinstance(message, str):
            logger.error("Invalid message format: expected JSON string")
            return

        try:
            # Parse the JSON string to validate its structure
            json_data = json.loads(message)

            if 'snapshots' not in json_data:
                logger.error("Invalid JSON structure: 'snapshots' key not found")
                return

            # Extract key from the JSON data or use a default
            key = json_data.get('key', f"default_key_{int(time.time() * 1000)}")

            # Send the JSON string directly to Kafka
            self.send_to_kafka("snapshots", key, message)

        except json.JSONDecodeError:
            logger.error("Invalid JSON format in the message")
        except Exception as e:
            logger.error(f"Error processing message: {e}")