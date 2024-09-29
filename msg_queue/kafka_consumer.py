from confluent_kafka import Consumer, KafkaException, KafkaError

# Kafka cluster configuration settings
kafka_brokers = '31.220.102.46:29092,31.220.102.46:29094'

consumer_conf = {
    'bootstrap.servers': kafka_brokers,
    'group.id': 'python-consumer-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'socket.timeout.ms': 10000,  # 10 seconds
}


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


if __name__ == '__main__':
    print("Kafka Consumer Started")
    print("Listening for messages... (Press Ctrl+C to exit)")
    consume_messages()
