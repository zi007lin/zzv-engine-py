import flatbuffers
import unittest
from schemas.snapshot import Snapshot, SnapshotList

# Helper function to serialize a SnapshotList
def serialize_snapshot_list(builder, snapshots, key, time, name):
    # Serialize each Snapshot object
    snapshot_offsets = []
    for snapshot in snapshots:
        # Serialize fields of Snapshot
        id_offset = builder.CreateString(snapshot['id'])
        data_offset = builder.CreateString(snapshot['data'])

        # Start and end the Snapshot object
        Snapshot.Start(builder)
        Snapshot.AddId(builder, id_offset)
        Snapshot.AddData(builder, data_offset)
        snapshot_offset = Snapshot.End(builder)
        snapshot_offsets.append(snapshot_offset)

    # Create the vector of Snapshots
    SnapshotList.StartSnapshotsVector(builder, len(snapshot_offsets))
    for offset in reversed(snapshot_offsets):
        builder.PrependUOffsetTRelative(offset)
    snapshots_vector = builder.EndVector()

    # Create other fields of SnapshotList
    key_offset = builder.CreateString(key)
    name_offset = builder.CreateString(name)

    # Build the SnapshotList table
    SnapshotList.Start(builder)
    SnapshotList.AddSnapshots(builder, snapshots_vector)
    SnapshotList.AddKey(builder, key_offset)
    SnapshotList.AddTime(builder, time)
    SnapshotList.AddName(builder, name_offset)
    snapshot_list = SnapshotList.End(builder)

    # Finish the builder and get the serialized data
    builder.Finish(snapshot_list)
    return builder.Output()

# Helper function to deserialize a SnapshotList
def deserialize_snapshot_list(buffer):
    # Deserialize buffer into a SnapshotList object
    snapshot_list = SnapshotList.SnapshotList.GetRootAsSnapshotList(buffer, 0)

    # Extract key, time, and name fields
    key = snapshot_list.Key().decode('utf-8')
    time = snapshot_list.Time()
    name = snapshot_list.Name().decode('utf-8')

    # Extract each Snapshot
    snapshots = []
    for i in range(snapshot_list.SnapshotsLength()):
        snapshot = snapshot_list.Snapshots(i)
        id = snapshot.Id().decode('utf-8')
        data = snapshot.Data().decode('utf-8')
        snapshots.append({'id': id, 'data': data})

    return {'key': key, 'time': time, 'name': name, 'snapshots': snapshots}

# Define unit test for SnapshotList serialization and deserialization
class TestSnapshotListSerialization(unittest.TestCase):
    def setUp(self):
        # Sample data to be serialized and deserialized
        self.snapshots = [
            {'id': 'snapshot_001', 'data': 'data_001'},
            {'id': 'snapshot_002', 'data': 'data_002'},
            {'id': 'snapshot_003', 'data': 'data_003'},
        ]
        self.key = 'unique-key-123'
        self.time = 1633072800  # Example timestamp (Unix time)
        self.name = 'TestSnapshotList'

    def test_snapshot_list_serialization(self):
        # Create a new FlatBuffer builder
        builder = flatbuffers.Builder(1024)

        # Serialize SnapshotList
        serialized_data = serialize_snapshot_list(builder, self.snapshots, self.key, self.time, self.name)

        # Deserialize the SnapshotList
        deserialized_data = deserialize_snapshot_list(serialized_data)

        # Assert that the key, time, and name are the same
        self.assertEqual(deserialized_data['key'], self.key)
        self.assertEqual(deserialized_data['time'], self.time)
        self.assertEqual(deserialized_data['name'], self.name)

        # Assert that the snapshots are the same
        self.assertEqual(len(deserialized_data['snapshots']), len(self.snapshots))
        for original, deserialized in zip(self.snapshots, deserialized_data['snapshots']):
            self.assertEqual(original['id'], deserialized['id'])
            self.assertEqual(original['data'], deserialized['data'])

if __name__ == '__main__':
    unittest.main()
