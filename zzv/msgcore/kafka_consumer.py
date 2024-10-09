import binascii
from SnapshotList import SnapshotList
from confluent_kafka import Consumer, KafkaError  # Assuming Kafka Consumer is used here


# Function to deserialize snapshot list from FlatBuffer
def deserialize_snapshot_list(buffer):
    try:
        snapshot_list = SnapshotList.GetRootAsSnapshotList(buffer, 0)
        key = snapshot_list.Key().decode('utf-8') if snapshot_list.Key() else None
        time = snapshot_list.Time()
        name = snapshot_list.Name().decode('utf-8') if snapshot_list.Name() else None

        snapshots = []
        for i in range(snapshot_list.SnapshotsLength()):
            snapshot = snapshot_list.Snapshots(i)
            id = snapshot.Id().decode('utf-8') if snapshot.Id() else None
            data = snapshot.Data().decode('utf-8') if snapshot.Data() else None
            snapshots.append({'id': id, 'data': data})

        return {'key': key, 'time': time, 'name': name, 'snapshots': snapshots}

    except Exception as e:
        print(f"Failed to deserialize FlatBuffer message: {e}")
        raise


# Function to compare buffers
def compare_buffers(test_buffer, kafka_buffer):
    if len(test_buffer) != len(kafka_buffer):
        print(f"Buffer sizes differ: test={len(test_buffer)}, kafka={len(kafka_buffer)}")
    else:
        print(f"Buffer sizes match: {len(test_buffer)}")

    print(f"Test Buffer Hexdump (first 64 bytes): {binascii.hexlify(test_buffer[:64])}")
    print(f"Kafka Buffer Hexdump (first 64 bytes): {binascii.hexlify(kafka_buffer[:64])}")

    for i, (t, k) in enumerate(zip(test_buffer, kafka_buffer)):
        if t != k:
            print(f"Byte {i} differs: test={hex(t)}, kafka={hex(k)}")

# Kafka cluster configuration settings
kafka_brokers = '31.220.102.46:29092,31.220.102.46:29094'

# Function to consume messages from Kafka
def consume_messages():
    consumer = Consumer({
        'bootstrap.servers': kafka_brokers,  # Change to your Kafka server address
        'group.id': 'test_group',
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe(['snapshots'])  # Subscribe to the topic

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Error consuming message: {msg.error()}")
                break

        flatbuffer_message = msg.value()
        print(f"Received message from Kafka (size {len(flatbuffer_message)}): {flatbuffer_message}")

        try:
            # Replace with the actual test message or load it as needed
            test_message = b'...'  # Load or define the test message used in your test
            print("Comparing Kafka message with test message:")
            compare_buffers(test_message, flatbuffer_message)

            deserialized_snapshot_list = deserialize_snapshot_list(flatbuffer_message)
            print(f"Deserialized SnapshotList from Kafka: {deserialized_snapshot_list}")

        except Exception as e:
            print(f"Failed to deserialize Kafka message: {e}")

    consumer.close()


# Main function definition
def main():
    print("Kafka Consumer Started")
    consume_messages()


# Entry point for script execution
if __name__ == "__main__":
    main()
