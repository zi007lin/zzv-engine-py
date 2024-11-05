import asyncio
import logging
import queue
from typing import Any, Optional, Dict

from fastapi import FastAPI

from zzv.common.constants import QUEUE_MANAGER
from zzv.engine.manager import Manager
from zzv.health.health_report import HealthReport
from zzv.health.status import Status
from zzv.msgcore.transporters.kafka_transporter import KafkaTransporter

logger = logging.getLogger(__name__)

class PrioritizedMessage:
    """Custom class to hold priority and message data for queue processing."""
    def __init__(self, priority: int, message_data: Any):
        self.priority = priority
        self.message_data = message_data

    def __lt__(self, other):
        return self.priority < other.priority


class QueueManager(Manager):
    def __init__(self, kernel, kafka_brokers: str):
        """Initialize the QueueManager and KafkaTransporter."""
        super().__init__(name="QueueManager")  # Initialize the base Manager class with the name attribute
        self.kernel = kernel
        self.sending_queue = queue.PriorityQueue()  # Priority queue for messages to be processed
        self._running = False
        self.kafka_transporter = KafkaTransporter(kafka_brokers)  # Initialize KafkaTransporter

        # Add attributes to track statistics
        self.stats = {
            "messages_enqueued": 0,  # Number of messages added to the queue
            "messages_processed": 0,  # Number of messages processed
            "messages_sent": 0  # Number of messages successfully sent
        }

    async def start(self):
        """Start the QueueManager and KafkaTransporter services asynchronously."""
        logger.info(f"Starting {QUEUE_MANAGER}...")
        self.kafka_transporter.start()  # Start KafkaTransporter
        self._running = True
        while self._running:
            try:
                # Process messages from the queue with a high-frequency timer
                await self.process_messages()
                await asyncio.sleep(1e-9)  # Sleep for a few nanoseconds
            except Exception as e:
                logger.error(f"Error in {QUEUE_MANAGER}: {e}")

    async def close(self):
        """Stop the QueueManager and KafkaTransporter services asynchronously."""
        logger.info(f"Stopping {QUEUE_MANAGER}...")
        self._running = False
        self.kafka_transporter.stop()  # Stop KafkaTransporter

    def handle_message(self, message_type: str, message_data: Any):
        """Handle incoming messages and add them to the queue."""
        # Add the message to the queue with a default priority of 0 for non-priority messages
        self.sending_queue.put(PrioritizedMessage(priority=0, message_data=message_data))
        self.stats["messages_enqueued"] += 1  # Update message enqueued count
        logger.info("Message added to the sending queue.")

    async def process_messages(self):
        """Process messages in the sending queue."""
        while not self.sending_queue.empty():
            try:
                message_item = self.sending_queue.get()
                self.stats["messages_processed"] += 1  # Update message processed count
                await self.route_message(message_item.message_data)
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def route_message(self, message: Any):
        """Route the message to the appropriate destination."""
        await self.kafka_transporter.route_message(message)  # Send to Kafka
        self.stats["messages_sent"] += 1  # Update message sent count
        logger.info("Routed message to Kafka...")


def _register_service(self, name: str, service: Any) -> None:
    """Register a service with the given name."""
    self._services[name] = service


def get_service(self, name: str) -> Optional[Any]:
    """Retrieve a registered service by name."""
    return self._services.get(name)


def get_health(self):
    """
    Return the health status of the QueueManager as a HealthReport object.
    """
    status = Status.OK if self._running else Status.ERROR
    return HealthReport(
        manager_name=self.name,
        status=status,
        details=[
            "QueueManager is healthy" if self._running else "QueueManager is not running.",
            f"Messages in queue: {self.sending_queue.qsize()}",
            f"Messages enqueued: {self.stats['messages_enqueued']}",
            f"Messages processed: {self.stats['messages_processed']}",
            f"Messages sent: {self.stats['messages_sent']}"
        ]
    )


def register_endpoints(self, app: FastAPI):
    """
    Register custom endpoints for the QueueManager.

    Args:
        app (FastAPI): The main FastAPI application where endpoints should be registered.
    """
    print("Registering endpoints for QueueManager...")

    # Register an endpoint to get QueueManager statistics
    @app.get(f"/{self.name}/stats")
    async def queue_manager_stats() -> Dict[str, Any]:
        """Get statistical information of the QueueManager."""
        return {
            "queue_size": self.sending_queue.qsize(),
            "messages_enqueued": self.stats["messages_enqueued"],
            "messages_processed": self.stats["messages_processed"],
            "messages_sent": self.stats["messages_sent"]
        }

    print(f"Registered endpoints for {self.name}.")

