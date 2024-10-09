import argparse
import time

import flatbuffers  # Import flatbuffers for serialization
from colorama import init, Fore
from confluent_kafka import Producer, KafkaException

from schemas.snapshot import Snapshot, SnapshotList  # Assuming snapshot schemas are available

init(autoreset=True)

# Kafka cluster configuration settings
kafka_brokers = '31.220.102.46:29092,31.220.102.46:29094'

producer_conf = {
    'bootstrap.servers': kafka_brokers,
    'client.id': 'python-producer',
    'acks': 'all',
    'retries': 5,
    'retry.backoff.ms': 500,
    'socket.timeout.ms': 10000,  # 10 seconds
}


# Delivery callback for producer to report the result of the produce request
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


# Serialization function copied from test_snapshotlist.py
def serialize_snapshot_list(builder, snapshots, key, time, name):
    snapshot_offsets = []
    for snapshot in snapshots:
        id_offset = builder.CreateString(snapshot['id'])
        data_offset = builder.CreateString(snapshot['data'])

        Snapshot.Start(builder)
        Snapshot.AddId(builder, id_offset)
        Snapshot.AddData(builder, data_offset)
        snapshot_offset = Snapshot.End(builder)
        snapshot_offsets.append(snapshot_offset)

    SnapshotList.StartSnapshotsVector(builder, len(snapshot_offsets))
    for offset in reversed(snapshot_offsets):
        builder.PrependUOffsetTRelative(offset)
    snapshots_vector = builder.EndVector()

    key_offset = builder.CreateString(key)
    name_offset = builder.CreateString(name)

    SnapshotList.Start(builder)
    SnapshotList.AddSnapshots(builder, snapshots_vector)
    SnapshotList.AddKey(builder, key_offset)
    SnapshotList.AddTime(builder, time)
    SnapshotList.AddName(builder, name_offset)
    snapshot_list = SnapshotList.End(builder)

    builder.Finish(snapshot_list)
    return builder.Output()


def create_and_send_snapshot_message(producer):
    # Sample data similar to the test in test_snapshotlist.py
    snapshots = [
        {'id': 'snapshot_001', 'data': 'data_001'},
        {'id': 'snapshot_002', 'data': 'data_002'},
        {'id': 'snapshot_003', 'data': 'data_003'},
    ]
    key = 'unique-key-123'
    time = 1633072800  # Example timestamp (Unix time)
    name = 'TestSnapshotList'

    # Create a new FlatBuffer builder
    builder = flatbuffers.Builder(1024)

    # Serialize SnapshotList
    serialized_data = serialize_snapshot_list(builder, snapshots, key, time, name)

    # Convert serialized_data (bytearray) to bytes
    serialized_data_bytes = bytes(serialized_data)

    # Produce the serialized message
    produce_message(producer, serialized_data_bytes, key)


def main():
    parser = argparse.ArgumentParser(description="Kafka Producer")
    parser.add_argument("--blast", type=int, help="Number of messages to blast")
    args = parser.parse_args()

    producer = Producer(producer_conf)

    if args.blast:
        print(Fore.CYAN + f"Kafka Producer Started - Blasting {args.blast} messages")
        for i in range(args.blast):
            create_and_send_snapshot_message(producer)
            time.sleep(1)  # Add sleep to simulate delay between messages
    else:
        print(Fore.CYAN + "Kafka Producer Started - Sending single serialized SnapshotList message")
        create_and_send_snapshot_message(producer)

    producer.flush(timeout=10)
    print(Fore.CYAN + "Message sending completed")


if __name__ == '__main__':
    main()
