import logging
from typing import Any, Dict, List

from fastapi import FastAPI
from zzv.common.constants import QUEUE_MANAGER, SNAPSHOT_LIST, MSG_MANAGER
from zzv.engine.manager import Manager
from zzv.health.health_report import HealthReport
from zzv.health.status import Status
from zzv.models.snapshot import SnapshotList

logger = logging.getLogger(__name__)


class MsgManager(Manager):
    def __init__(self, kernel):
        """Initialize the MsgManager with a reference to the Kernel."""
        super().__init__(name="MsgManager")  # Initialize the base Manager class with the name attribute
        self.kernel = kernel
        self._services: Dict[str, Any] = {}
        self._running = False

        # Add attributes to track message statistics
        self.stats = {
            "messages_handled": 0,  # Number of messages handled
            "messages_routed": 0,  # Number of messages routed to other managers
            "error_count": 0  # Number of errors encountered during message handling
        }

        # Maintain a list of recently processed messages (for debugging or auditing)
        self.recent_messages: List[Any] = []

        # Define message handlers for specific message types
        self.message_handlers = {
            'SnapshotList': self.handle_snapshot_list_message,
            # Add other message types and their handlers here
        }

    async def start(self):
        """Start the MsgManager service asynchronously."""
        logger.info(f"Starting {MSG_MANAGER}...")
        self._running = True

    async def close(self):
        """Stop the MsgManager service asynchronously."""
        logger.info(f"Stopping {MSG_MANAGER}...")
        self._running = False

    def handle_message(self, message_type: str, message_data: Any):
        """Handle incoming messages based on their type."""
        handler = self.message_handlers.get(message_type)
        if handler:
            handler(message_data)
            self.stats["messages_handled"] += 1  # Update message handled count
            self.recent_messages.append(message_data)  # Store message for auditing
            logger.info(f"Handled message of type: {message_type}")
        else:
            self.stats["error_count"] += 1  # Update error count if no handler found
            logger.warning(f"No handler found for message type: {message_type}")

    def handle_snapshot_list_message(self, message_data: SnapshotList):
        """Handle SnapshotList messages and route them to the QueueManager."""
        try:
            # Access QueueManager through the Kernel with access validation
            queue_manager = self.kernel.get_service(QUEUE_MANAGER, caller=self)
            if queue_manager:
                queue_manager.handle_message(SNAPSHOT_LIST, message_data)
                self.stats["messages_routed"] += 1  # Update message routed count
                logger.info(f"{SNAPSHOT_LIST} message routed to {QUEUE_MANAGER}.")
            else:
                self.stats["error_count"] += 1  # Update error count if QueueManager is not accessible
                logger.error(f"{QUEUE_MANAGER} is not accessible.")
        except Exception as e:
            logger.error(f"Error handle_snapshot_list_message: {e}")

    def get_health(self):
        """
        Return the health status of the MsgManager as a HealthReport object.
        """
        status = Status.OK if self._running else Status.ERROR
        return HealthReport(
            manager_name=self.name,
            status=status,
            details=["MsgManager is healthy" if self._running else "MsgManager is not running."]
        )

    def register_endpoints(self, app: FastAPI):
        """
        Register custom endpoints for the MsgManager.

        Args:
            app (FastAPI): The main FastAPI application where endpoints should be registered.
        """

        # Register an endpoint to get statistics of MsgManager
        @app.get(f"/{self.name}/stats")
        async def msg_manager_stats() -> Dict[str, Any]:
            """Get statistical information of the MsgManager."""
            return self.stats

        # Register an endpoint to get recent messages handled by the MsgManager
        @app.get(f"/{self.name}/recent-messages")
        async def recent_messages() -> List[Any]:
            """Get the list of recently handled messages."""
            return self.recent_messages

        # Register an endpoint to list message handlers and their status
        @app.get(f"/{self.name}/handlers")
        async def message_handlers_info() -> Dict[str, bool]:
            """Get information about active message handlers."""
            return {handler_name: True for handler_name in self.message_handlers}

        print(f"Registered endpoints for {self.name}.")
