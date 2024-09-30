import unittest
from io import StringIO

import pandas as pd

# Import the Snapshot and SnapshotList classes from your module
from zzv.models import Snapshot, SnapshotList  # Replace 'your_module' with the actual module name


class TestSnapshotParsing(unittest.TestCase):
    def test_csv_to_snapshot_list(self):
        # CSV data as a string
        csv_data = '''zb1BarsC9,zb1SideC10,zb1iMarkC11,zb1PnLC12,Symbol
1.0,-1.0,118.98,0.02,NVDA
2.0,1.0,19.66,0.01,INTC
2.0,1.0,15,0.05,KEYS
1.0,-1.0,210.45,0.14,FFIV
2.0,-1.0,752.73,1.23,KLAC
8.0,1.0,182.34,0.47,VRSN
1.0,-1.0,442.38,0.62,MSI
'''

        # Read the CSV data into a pandas DataFrame
        csv_file_like = StringIO(csv_data)
        df = pd.read_csv(csv_file_like)

        # Initialize an empty list to hold Snapshot objects
        snapshot_list = []

        # Iterate over each row in the DataFrame
        for index, row in df.iterrows():
            # Convert the row to a dictionary
            message_data = row.to_dict()

            # Create a Snapshot object using the message_data
            snapshot = Snapshot(**message_data)

            # Add the Snapshot object to the list
            snapshot_list.append(snapshot)

        # Create a SnapshotList object
        snapshot_list_message = SnapshotList(snapshots=snapshot_list)

        # Perform assertions to check that the data is as expected
        self.assertEqual(len(snapshot_list_message.snapshots), 7)

        # Test the first snapshot
        snapshot = snapshot_list_message.snapshots[0]
        self.assertEqual(snapshot.zb1BarsC9, 1.0)
        self.assertEqual(snapshot.zb1SideC10, -1.0)
        self.assertEqual(snapshot.zb1iMarkC11, 118.98)
        self.assertEqual(snapshot.zb1PnLC12, 0.02)
        self.assertEqual(snapshot.Symbol, 'NVDA')

        # Test the third snapshot (KEYS)
        snapshot = snapshot_list_message.snapshots[2]
        self.assertEqual(snapshot.zb1BarsC9, 2.0)
        self.assertEqual(snapshot.zb1SideC10, 1.0)
        self.assertEqual(snapshot.zb1iMarkC11, 15)
        self.assertEqual(snapshot.zb1PnLC12, 0.05)
        self.assertEqual(snapshot.Symbol, 'KEYS')

        # Test the last snapshot
        snapshot = snapshot_list_message.snapshots[6]
        self.assertEqual(snapshot.zb1BarsC9, 1.0)
        self.assertEqual(snapshot.zb1SideC10, -1.0)
        self.assertEqual(snapshot.zb1iMarkC11, 442.38)
        self.assertEqual(snapshot.zb1PnLC12, 0.62)
        self.assertEqual(snapshot.Symbol, 'MSI')

        # Optionally, print the SnapshotList for visual inspection
        print(snapshot_list_message)


if __name__ == '__main__':
    unittest.main()
