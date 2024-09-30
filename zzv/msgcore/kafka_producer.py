import argparse
import time

from colorama import init, Fore
from confluent_kafka import Producer, KafkaException

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


def blast_messages(count, sleep_time):
    producer = Producer(producer_conf)
    print(Fore.CYAN + f"Kafka Producer Started - Blasting {count} messages")

    for i in range(count):
        message = f"Test message {i + 1}"
        key = f"key_{i + 1}"
        produce_message(producer, message, key)
        time.sleep(sleep_time)  # Sleep for specified time

    producer.flush(timeout=10)
    print(Fore.CYAN + "Message blasting completed")


def interactive_mode():
    producer = Producer(producer_conf)
    print(Fore.CYAN + "Kafka Producer Started - Interactive Mode")
    print(Fore.YELLOW + "Enter 'Y' to send a new message, 'B' to blast messages, or 'X' to exit")

    while True:
        user_input = input().strip().upper()
        if user_input == 'X':
            break
        elif user_input == 'Y':
            message = input("Enter your message: ")
            produce_message(producer, message, 'interactive_key')
            producer.flush(timeout=10)
        elif user_input == 'B':
            count = int(input("Enter number of messages to blast: "))
            blast_messages(count, 1e-9)  # 1 nanosecond sleep
        else:
            print(Fore.YELLOW + "Invalid input. Enter 'Y' to send a new message, 'B' to blast messages, or 'X' to exit")

    print(Fore.CYAN + "Producer terminated")


def main():
    parser = argparse.ArgumentParser(description="Kafka Producer")
    parser.add_argument("--blast", type=int, help="Number of messages to blast")
    args = parser.parse_args()

    if args.blast:
        blast_messages(args.blast, 1e-9)  # 1 nanosecond sleep
    else:
        interactive_mode()


if __name__ == '__main__':
    main()
