import flatbuffers
from schemas.snapshot.Snapshot import Snapshot  # Adjust the import as per your structure
from schemas.snapshot.SnapshotList import SnapshotList  # Adjust the import as per your structure
from protocol_interface import ProtocolInterface

class FlatBuffersProtocol(ProtocolInterface):
    def serialize(self, obj) -> bytes:
        """Serialize a FlatBuffers object to bytes."""
        builder = flatbuffers.Builder(1024)
        # Assume `obj` is of type `SnapshotList`
        builder.Finish(obj)
        return bytes(builder.Output())

    def deserialize(self, data: bytes):
        """Deserialize bytes to a FlatBuffers object."""
        return SnapshotList.GetRootAs(data, 0)

    def build_flatbuffers_offsets(self, builder, parsed_csv_rows):
        """Build FlatBuffers offsets for the given parsed CSV rows."""
        # Create a list of offsets for the Snapshot objects
        snapshot_offsets = []

        for row in parsed_csv_rows:
            # Replace incorrect values using correction mappings if available
            id_value = row.get('zb1BarsC9', '')
            data_value = row.get('Symbol', '')

            id_offset = builder.CreateString(id_value)
            data_offset = builder.CreateString(data_value)

            # Create a Snapshot object
            Snapshot.Start(builder)
            Snapshot.AddId(builder, id_offset)
            Snapshot.AddData(builder, data_offset)
            snapshot_offset = Snapshot.End(builder)

            # Append to the list of snapshot offsets
            snapshot_offsets.append(snapshot_offset)

        # Create a vector of Snapshots
        SnapshotList.StartSnapshotsVector(builder, len(snapshot_offsets))
        for snapshot_offset in snapshot_offsets:
            builder.PrependUOffsetTRelative(snapshot_offset)
        snapshots_vector = builder.EndVector()

        # Create the SnapshotList object
        key_offset = builder.CreateString("unique-key-123")  # Replace with actual key if available
        name_offset = builder.CreateString("XLK")  # Default name

        SnapshotList.Start(builder)
        SnapshotList.AddSnapshots(builder, snapshots_vector)
        SnapshotList.AddKey(builder, key_offset)
        SnapshotList.AddTime(builder, 1638316800000)  # Example timestamp in milliseconds
        SnapshotList.AddName(builder, name_offset)
        snapshot_list = SnapshotList.End(builder)

        # Finalize the buffer and get the byte array
        return snapshot_list
