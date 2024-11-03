from abc import abstractmethod
from zzv.engine.manager import Manager  # Import the existing Manager class
from typing import Optional, Dict, Any
from zzv.msgcore.kafka_topic_manager import KafkaTopicManager
from zzv.msgcore.protocol_interface import ProtocolInterface

class KernelAwareManager(Manager):
    """
    Interface for managers that need to be aware of the Kernel.
    """

    @abstractmethod
    def set_kernel(self, kernel):
        """
        Set the Kernel instance for the manager.

        Args:
            kernel (Kernel): The kernel instance to be set.
        """
        pass
