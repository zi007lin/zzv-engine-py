import argparse
import time

import flatbuffers
from colorama import init, Fore
from confluent_kafka import Producer, KafkaException

from schemas.snapshot import Snapshot, SnapshotList
import time
init(autoreset=True)

kafka_brokers = '31.220.102.46:29092,31.220.102.46:29094'

producer_conf = {
    'bootstrap.servers': kafka_brokers,
    'client.id': 'python-producer',
    'acks': 'all',
    'retries': 5,
    'retry.backoff.ms': 500,
    'socket.timeout.ms': 10000,
}


def delivery_report(err, msg):
    if err is not None:
        print(Fore.RED + f"Delivery failed for message {msg.key()}: {err}")
    else:
        print(Fore.GREEN + f"Message {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}]")


def produce_message(producer, message, key):
    try:
        producer.produce('snapshots', key=key, value=message, callback=delivery_report)
        producer.poll(0)
    except KafkaException as e:
        print(Fore.RED + f"Error while producing: {e}")


def serialize_snapshot_list(snapshots, key, time, name):
    builder = flatbuffers.Builder(1024)
    snapshot_offsets = []

    for snapshot in snapshots:
        timestamp_offset = builder.CreateString(snapshot['Timestamp'])
        symbol_offset = builder.CreateString(snapshot['Symbol'])

        Snapshot.SnapshotStart(builder)
        Snapshot.SnapshotAddTimestamp(builder, timestamp_offset)
        Snapshot.SnapshotAddZb1BarsC9(builder, snapshot['zb1BarsC9'])
        Snapshot.SnapshotAddZb1SideC10(builder, snapshot['zb1SideC10'])
        Snapshot.SnapshotAddZb1MarkC11(builder, snapshot['zb1MarkC11'])
        Snapshot.SnapshotAddZb1PnlC12(builder, snapshot['zb1PnLC12'])
        Snapshot.SnapshotAddSymbol(builder, symbol_offset)
        snapshot_offset = Snapshot.SnapshotEnd(builder)
        snapshot_offsets.append(snapshot_offset)

    SnapshotList.SnapshotListStartSnapshotsVector(builder, len(snapshot_offsets))
    for offset in reversed(snapshot_offsets):
        builder.PrependUOffsetTRelative(offset)
    snapshots_vector = builder.EndVector()

    key_offset = builder.CreateString(key)
    name_offset = builder.CreateString(name)

    SnapshotList.SnapshotListStart(builder)
    SnapshotList.SnapshotListAddSnapshots(builder, snapshots_vector)
    SnapshotList.SnapshotListAddKey(builder, key_offset)
    SnapshotList.SnapshotListAddTime(builder, time)
    SnapshotList.SnapshotListAddName(builder, name_offset)
    snapshot_list = SnapshotList.SnapshotListEnd(builder)

    builder.Finish(snapshot_list)
    return builder.Output()


def create_and_send_snapshot_message(producer):
    snapshots = [
        {'Timestamp': '1702132066', 'zb1BarsC9': 5.0, 'zb1SideC10': -1.0, 'zb1MarkC11': 134.68,
         'zb1PnLC12': 0.54, 'Symbol': 'NVDA'},
        {'Timestamp': '2702132066', 'zb1BarsC9': 3.0, 'zb1SideC10': 1.0, 'zb1MarkC11': 45.69,
         'zb1PnLC12': 0.16, 'Symbol': 'SMCI'}
    ]
    key = 'unique-key-123'
    time = f"1702132066"
    name = 'TestSnapshotList'

    serialized_data = serialize_snapshot_list(snapshots, key, time, name)
    produce_message(producer, serialized_data, key)


def main():
    parser = argparse.ArgumentParser(description="Kafka Producer")
    parser.add_argument("--blast", type=int, help="Number of messages to blast")
    args = parser.parse_args()

    producer = Producer(producer_conf)

    if args.blast:
        print(Fore.CYAN + f"Kafka Producer Started - Blasting {args.blast} messages")
        for i in range(args.blast):
            create_and_send_snapshot_message(producer)
            time.sleep(1)
    else:
        print(Fore.CYAN + "Kafka Producer Started - Sending single serialized SnapshotList message")
        create_and_send_snapshot_message(producer)

    producer.flush(timeout=10)
    print(Fore.CYAN + "Message sending completed")


if __name__ == '__main__':
    main()
