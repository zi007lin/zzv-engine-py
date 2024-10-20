import json
import logging

from colorama import init, Fore
from confluent_kafka import Producer, KafkaException
from pydantic.v1.validators import validate_json

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

    def ensure_dict(self, message):
        """
        Ensure that the message is a dictionary.
        If it's a string, attempt to parse it as JSON.

        :param message: The input message (could be dict or str)
        :return: tuple (dict or None, str), (parsed_message, error_message)
        """
        if isinstance(message, dict):
            return message, ""
        elif isinstance(message, str):
            try:
                return json.loads(message), ""
            except json.JSONDecodeError as e:
                return None, f"Invalid JSON string: {e}"
        else:
            return None, f"Unsupported message type: {type(message)}"

    def validate_message(self, message):
        """
        Validate the required fields in the message.

        :param message: dict, the message to validate
        :return: tuple (bool, str), (is_valid, error_message)
        """
        required_fields = ['topic', 'key']

        for field in required_fields:
            if field not in message:
                return False, f"Missing required field: {field}"

            if not message[field]:
                return False, f"Empty value for required field: {field}"

        return True, ""

    async def route_message(self, message):
        """
        Process the message after ensuring it's a dict and validating its contents.

        :param message: The input message (could be dict or str)
        """
        # First, ensure the message is a dictionary
        parsed_message, parse_error = self.ensure_dict(message)
        if parsed_message is None:
            logging.error(f"Failed to parse message: {parse_error}")
            return

        # Now validate the contents
        is_valid, error_message = self.validate_message(parsed_message)
        if not is_valid:
            logging.error(f"Invalid message: {error_message}")
            return

        # If we're here, we have a valid dictionary with required fields
        topic = parsed_message['topic']
        key = parsed_message['key']
        self.send_to_kafka(topic, key, json.dumps(message))

