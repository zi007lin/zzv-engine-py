from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, ConfigResource, ConfigSource
from confluent_kafka.cimpl import NewTopic


class KafkaTopicManager:
    def __init__(self, bootstrap_servers):
        """
        Initialize Kafka Admin client with the provided bootstrap servers.

        Args:
            bootstrap_servers (str): Comma-separated list of Kafka bootstrap servers.
        """
        self.admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
        self.default_num_partitions = 11

    def create_topic(self, topic_name, num_partitions=None, replication_factor=1, retention_ms=None):
        """
        Create a Kafka topic.

        Args:
            topic_name (str): Name of the topic to be created.
            num_partitions (int): Number of partitions for the topic. Defaults to self.default_num_partitions.
            replication_factor (int): Replication factor for the topic.
            retention_ms (int): Message retention time in milliseconds. If None, the broker default is used.
        """
        if num_partitions is None:
            num_partitions = self.default_num_partitions

        config = {}
        if retention_ms is not None:
            config['retention.ms'] = str(retention_ms)

        new_topic = NewTopic(topic_name, num_partitions, replication_factor, config=config)
        fs = self.admin_client.create_topics([new_topic])

        for topic, f in fs.items():
            try:
                f.result()
                print(f"Topic '{topic}' created successfully.")
            except Exception as e:
                print(f"Failed to create topic '{topic}': {e}")

    def delete_topics(self, topic_names):
        """
        Delete multiple Kafka topics.

        Args:
            topic_names (list): List of topic names to be deleted.
        """
        fs = self.admin_client.delete_topics(topic_names, operation_timeout=30)

        for topic, f in fs.items():
            try:
                f.result()
                print(f"Topic '{topic}' deleted successfully.")
            except Exception as e:
                print(f"Failed to delete topic '{topic}': {e}")

    def list_topics(self):
        """
        List all topics in the Kafka cluster.

        Returns:
            list: List of topic names.
        """
        return list(self.admin_client.list_topics().topics.keys())

    def get_topic_config(self, topic_name):
        """
        Get the configuration of a specific topic.

        Args:
            topic_name (str): Name of the topic.

        Returns:
            dict: Topic configuration.
        """
        resource = ConfigResource('topic', topic_name)
        fs = self.admin_client.describe_configs([resource])

        for res, f in fs.items():
            try:
                configs = f.result()
                return {config.name: config.value for config in configs.values() if
                        config.source == ConfigSource.DYNAMIC_TOPIC_CONFIG}
            except KafkaException as e:
                print(f"Failed to get config for topic '{topic_name}': {e}")
                return None


if __name__ == "__main__":
    # Use localhost if connecting from the host machine
    kafka_servers = '31.220.102.46:29092,31.220.102.46:29094'
    manager = KafkaTopicManager(kafka_servers)

    # Create a topic for strategy data with 30-day retention
    manager.create_topic('strategy_data',
                         num_partitions=11,
                         replication_factor=1,
                         retention_ms=2592000000,  # 30 days
                         config={
                             "cleanup.policy": "delete",
                             "segment.ms": 86400000,  # 1 day segment size
                             "min.compaction.lag.ms": 3600000  # 1 hour minimum message age before compaction
                         })
    # List topics
    print("Topics:", manager.list_topics())

    # Get topic config
    print("Snapshots config:", manager.get_topic_config('snapshots'))

    # Delete multiple topics
    # manager.delete_topics(['snapshots', 'another_topic'])
