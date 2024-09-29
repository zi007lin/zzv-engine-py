from confluent_kafka.admin import AdminClient, NewTopic


class KafkaTopicManager:
    def __init__(self, bootstrap_servers):
        """
        Initialize Kafka Admin client with the provided bootstrap servers.

        Args:
            bootstrap_servers (str): Comma-separated list of Kafka bootstrap servers.
        """
        self.admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})

    def create_topic(self, topic_name, num_partitions=1, replication_factor=1):
        """
        Create a Kafka topic.

        Args:
            topic_name (str): Name of the topic to be created.
            num_partitions (int): Number of partitions for the topic.
            replication_factor (int): Replication factor for the topic.
        """
        new_topic = NewTopic(topic_name, num_partitions, replication_factor)
        fs = self.admin_client.create_topics([new_topic])

        for topic, f in fs.items():
            try:
                f.result()
                print(f"Topic '{topic}' created successfully.")
            except Exception as e:
                print(f"Failed to create topic '{topic}': {e}")

    def delete_topic(self, topic_name):
        """
        Delete a Kafka topic.

        Args:
            topic_name (str): Name of the topic to be deleted.
        """
        fs = self.admin_client.delete_topics([topic_name], operation_timeout=30)

        for topic, f in fs.items():
            try:
                f.result()
                print(f"Topic '{topic}' deleted successfully.")
            except Exception as e:
                print(f"Failed to delete topic '{topic}': {e}")


if __name__ == "__main__":
    # Use localhost if connecting from the host machine
    kafka_servers = '172.19.0.2:9092,172.19.0.3:9094'
    manager = KafkaTopicManager(kafka_servers)

    # Create a topic
    manager.create_topic('snapshots', num_partitions=1, replication_factor=1)
    # Delete a topic:
    # manager.delete_topic('snapshots')
