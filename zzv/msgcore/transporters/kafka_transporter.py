import json
import logging

from colorama import init, Fore
from confluent_kafka import Producer, KafkaException

init(autoreset=True)

logger = logging.getLogger(__name__)


class KafkaTransporter:
    def __init__(self, kafka_brokers: str):
        self.sector_map = {
            'XLK': 0, 'XLV': 1, 'XLF': 2, 'XLY': 3, 'XLI': 4,
            'XLP': 5, 'XLE': 6, 'XLU': 7, 'XLB': 8, 'XLC': 9, 'XLRE': 10
        }
        self.num_partitions = 11  # Total number of partitions

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

    def get_partition(self, key: str):
        if key in self.sector_map:
            return self.sector_map[key]
        return hash(key) % self.num_partitions

    def send_to_kafka(self, topic: str, key: str, message: str):
        if not self.producer:
            logger.error("Kafka Producer is not initialized.")
            return

        try:
            partition = self.get_partition(key)
            self.producer.produce(
                topic,
                key=key.encode('utf-8'),
                value=message.encode('utf-8'),
                partition=partition,
                callback=self.delivery_report
            )
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
            json_data = json.loads(message)

            topic = json_data.get('topic', "there is no topic provided!!!")
            if topic.endswith("!!!"):
                logger.error(f"Error detected: {topic}")
                return  # Exit the function if topic is an error

            key = json_data.get('key', "there is no key record provided!!!")
            if key.endswith("!!!"):
                logger.error(f"Error detected: {key}")
                return  # Exit the function if key is an error

            if key not in self.sector_map:
                logger.warning(f"Key '{key}' is not a recognized sector. Using default partitioning.")

            self.send_to_kafka(topic, key, message)

        except json.JSONDecodeError:
            logger.error("Invalid JSON format in the message")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
