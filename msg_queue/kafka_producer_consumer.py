import time

from confluent_kafka import Producer, Consumer, KafkaException, KafkaError

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

consumer_conf = {
    'bootstrap.servers': kafka_brokers,
    'group.id': 'python-consumer-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'socket.timeout.ms': 10000,  # 10 seconds
}


# Kafka Producer
def produce_messages():
    producer = Producer(producer_conf)
    try:
        for _ in range(5):  # Try 5 times
            try:
                producer.produce('snapshots', key='snapshot_key', value='snapshot_data', callback=delivery_report)
                producer.poll(0)
                break  # If successful, break the loop
            except KafkaException as e:
                print(f"Error while producing: {e}")
                time.sleep(1)  # Wait for 1 second before retrying
        producer.flush(timeout=10)
    except Exception as e:
        print(f"Unexpected error: {e}")


# Delivery callback for producer to report the result of the produce request
def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for message {msg.key()}: {err}")
    else:
        print(f"Message {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}]")


# Kafka Consumer
def consume_messages():
    consumer = Consumer(consumer_conf)
    consumer.subscribe(['snapshots'])

    try:
        while True:
            try:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Error consuming message: {msg.error()}")
                        break
                print(f"Received message: {msg.value().decode('utf-8')}")
                consumer.commit(message=msg)
            except KafkaException as e:
                print(f"Kafka error: {e}")
    except KeyboardInterrupt:
        print("Aborted by user")
    finally:
        consumer.close()


def main():
    print("Starting producer...")
    produce_messages()
    time.sleep(5)  # Wait for 5 seconds
    print("Starting consumer...")
    consume_messages()


if __name__ == '__main__':
    main()
