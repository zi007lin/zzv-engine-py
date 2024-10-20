from abc import ABC, abstractmethod


class ProtocolInterface(ABC):
    @abstractmethod
    def serialize(self, obj) -> bytes:
        """Serialize the given object to bytes."""
        pass

    @abstractmethod
    def deserialize(self, data: bytes):
        """Deserialize bytes to the corresponding object."""
        pass

    @abstractmethod
    def build_flatbuffers_offsets(self, builder, parsed_csv_rows):
        """Build FlatBuffers offsets for the given data."""
        pass
