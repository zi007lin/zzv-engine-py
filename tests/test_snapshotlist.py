import unittest

import flatbuffers
import pytest

from schemas.snapshot.Snapshot import SnapshotStart, SnapshotAddTimestamp, SnapshotAddZb1BarsC9, SnapshotAddZb1SideC10, \
    SnapshotAddZb1MarkC11, SnapshotAddZb1PnlC12, SnapshotAddSymbol, SnapshotEnd
from schemas.snapshot.SnapshotList import SnapshotList


def create_snapshot(builder, timestamp, zb1BarsC9, zb1SideC10, zb1MarkC11, zb1PnlC12, symbol):
    # Convert strings to offsets
    timestamp_offset = builder.CreateString(timestamp)
    symbol_offset = builder.CreateString(symbol)

    # Start building the Snapshot table
    SnapshotStart(builder)
    SnapshotAddTimestamp(builder, timestamp_offset)
    SnapshotAddZb1BarsC9(builder, zb1BarsC9)
    SnapshotAddZb1SideC10(builder, zb1SideC10)
    SnapshotAddZb1MarkC11(builder, zb1MarkC11)
    SnapshotAddZb1PnlC12(builder, zb1PnlC12)
    SnapshotAddSymbol(builder, symbol_offset)

    # Finish building the Snapshot table and return the offset
    return SnapshotEnd(builder)


from schemas.snapshot.SnapshotList import SnapshotListStart, SnapshotListStartSnapshotsVector, SnapshotListAddSnapshots, \
    SnapshotListAddKey, SnapshotListAddTime, SnapshotListAddName, SnapshotListEnd


def serialize_snapshot_list(builder, snapshots, key, time, name):
    snapshot_offsets = []
    for s in snapshots:
        snapshot_offsets.append(
            create_snapshot(builder, s['Timestamp'], s['zb1BarsC9'], s['zb1SideC10'], s['zb1MarkC11'], s['zb1PnLC12'],
                            s['Symbol']))

    # Create the snapshots vector
    SnapshotListStartSnapshotsVector(builder, len(snapshot_offsets))
    for offset in reversed(snapshot_offsets):
        builder.PrependUOffsetTRelative(offset)
    snapshots_vector = builder.EndVector()

    # Convert strings to offsets
    key_offset = builder.CreateString(key)
    name_offset = builder.CreateString(name)

    # Create the SnapshotList
    SnapshotListStart(builder)
    SnapshotListAddSnapshots(builder, snapshots_vector)
    SnapshotListAddKey(builder, key_offset)
    SnapshotListAddTime(builder, time)
    SnapshotListAddName(builder, name_offset)
    snapshot_list = SnapshotListEnd(builder)

    builder.Finish(snapshot_list)
    return builder.Output()


# Helper function to deserialize SnapshotList
def deserialize_snapshot_list(serialized_data):
    buf = bytearray(serialized_data)
    snapshot_list = SnapshotList.GetRootAsSnapshotList(buf, 0)

    # Deserialize snapshots
    snapshots = []
    for i in range(snapshot_list.SnapshotsLength()):
        snapshot = snapshot_list.Snapshots(i)
        snapshots.append({
            'Timestamp': snapshot.Timestamp().decode('utf-8'),
            'zb1BarsC9': snapshot.Zb1BarsC9(),
            'zb1SideC10': snapshot.Zb1SideC10(),
            'zb1MarkC11': snapshot.Zb1MarkC11(),
            'zb1PnLC12': snapshot.Zb1PnlC12(),
            'Symbol': snapshot.Symbol().decode('utf-8')
        })

    # Return the deserialized dictionary
    return {
        'snapshots': snapshots,
        'key': snapshot_list.Key().decode('utf-8'),
        'time': snapshot_list.Time(),
        'name': snapshot_list.Name().decode('utf-8')
    }


# Test case for SnapshotList serialization and deserialization
class TestSnapshotListSerialization(unittest.TestCase):

    def setUp(self):
        # Set up initial data for testing
        self.snapshots = [
            {'Timestamp': '2024-10-09T08:28:46.968Z', 'zb1BarsC9': 5.0, 'zb1SideC10': -1.0, 'zb1MarkC11': 134.68,
             'zb1PnLC12': 0.54, 'Symbol': 'NVDA'},
            {'Timestamp': '2024-10-09T08:28:46.968Z', 'zb1BarsC9': 3.0, 'zb1SideC10': 1.0, 'zb1MarkC11': 45.69,
             'zb1PnLC12': 0.16, 'Symbol': 'SMCI'}
        ]
        self.key = 'test_key'
        self.time = 1696843726968
        self.name = 'snapshot_test'

    def test_snapshot_list_serialization(self):
        # Create a new FlatBuffer builder
        builder = flatbuffers.Builder(1024)

        # Serialize SnapshotList
        serialized_data = serialize_snapshot_list(builder, self.snapshots, self.key, self.time, self.name)

        # Deserialize the SnapshotList
        deserialized_data = deserialize_snapshot_list(serialized_data)

        # Convert byte strings to regular strings for comparison
        deserialized_key = deserialized_data['key'].decode('utf-8') if isinstance(deserialized_data['key'], bytes) else \
        deserialized_data['key']
        deserialized_name = deserialized_data['name'].decode('utf-8') if isinstance(deserialized_data['name'],
                                                                                    bytes) else deserialized_data[
            'name']

        # Assert that the key, time, and name are the same
        assert deserialized_key == self.key
        assert deserialized_data['time'] == self.time
        assert deserialized_name == self.name

        # Assert that the snapshots are the same
        assert len(deserialized_data['snapshots']) == len(self.snapshots)
        for original, deserialized in zip(self.snapshots, deserialized_data['snapshots']):
            # Convert deserialized fields from bytes to string if necessary
            deserialized_timestamp = deserialized['Timestamp'].decode('utf-8') if isinstance(deserialized['Timestamp'],
                                                                                             bytes) else deserialized[
                'Timestamp']
            deserialized_symbol = deserialized['Symbol'].decode('utf-8') if isinstance(deserialized['Symbol'],
                                                                                       bytes) else deserialized[
                'Symbol']

            assert original['Timestamp'] == deserialized_timestamp
            assert original['zb1BarsC9'] == pytest.approx(deserialized['zb1BarsC9'])
            assert original['zb1SideC10'] == pytest.approx(deserialized['zb1SideC10'])
            assert original['zb1MarkC11'] == pytest.approx(deserialized['zb1MarkC11'])
            assert original['zb1PnLC12'] == pytest.approx(deserialized['zb1PnLC12'])
            assert original['Symbol'] == deserialized_symbol


# Run the tests
if __name__ == '__main__':
    unittest.main()
