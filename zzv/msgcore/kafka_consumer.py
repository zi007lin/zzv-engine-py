import json
import logging
import flatbuffers
from confluent_kafka import Consumer, KafkaError
from schemas.snapshot.SnapshotList import SnapshotListStart, SnapshotListAddKey, SnapshotListAddTime, \
    SnapshotListAddName, SnapshotListAddSnapshots, SnapshotListEnd, SnapshotListStartSnapshotsVector
from schemas.snapshot.Snapshot import SnapshotStart, SnapshotAddTimestamp, SnapshotAddZb1BarsC9, SnapshotAddZb1SideC10, \
    SnapshotAddZb1MarkC11, SnapshotAddZb1PnlC12, SnapshotAddSymbol, SnapshotEnd

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def process_incomplete_json(incomplete_json):
    try:
        # Attempt to parse the incomplete JSON
        parsed_data = json.loads(incomplete_json + "}")  # Add a closing brace
    except json.JSONDecodeError:
        try:
            # If that fails, try to parse just the complete part
            parsed_data = json.loads(incomplete_json.rsplit(',', 1)[0] + "]}")
        except json.JSONDecodeError:
            logger.error("Unable to parse the incomplete JSON")
            return None

    # Log the recovered data
    logger.warning(f"Recovered partial data from incomplete JSON: {parsed_data}")
    return parsed_data


def json_to_flatbuffer(json_data):
    try:
        # Parse the JSON string into a Python dictionary
        data = json.loads(json_data)

        # Validate the structure of the deserialized data
        if not all(key in data for key in ['key', 'time', 'name', 'snapshots']):
            raise ValueError("Missing required fields in the JSON data")

        # Create a FlatBuffer builder
        builder = flatbuffers.Builder(1024)

        # Create snapshots
        snapshot_offsets = []
        for snapshot in data['snapshots']:
            timestamp = builder.CreateString(snapshot['Timestamp'])
            symbol = builder.CreateString(snapshot['Symbol'])

            SnapshotStart(builder)
            SnapshotAddTimestamp(builder, timestamp)
            SnapshotAddZb1BarsC9(builder, snapshot['zb1BarsC9'])
            SnapshotAddZb1SideC10(builder, snapshot['zb1SideC10'])
            SnapshotAddZb1MarkC11(builder, snapshot['zb1MarkC11'])
            SnapshotAddZb1PnlC12(builder, snapshot['zb1PnLC12'])
            SnapshotAddSymbol(builder, symbol)
            snapshot_offsets.append(SnapshotEnd(builder))

        # Create snapshots vector
        SnapshotListStartSnapshotsVector(builder, len(snapshot_offsets))
        for offset in reversed(snapshot_offsets):
            builder.PrependUOffsetTRelative(offset)
        snapshots = builder.EndVector()

        # Create strings
        key = builder.CreateString(data['key'])
        name = builder.CreateString(data['name'])

        # Create SnapshotList
        SnapshotListStart(builder)
        SnapshotListAddKey(builder, key)
        SnapshotListAddTime(builder, data['time'])
        SnapshotListAddName(builder, name)
        SnapshotListAddSnapshots(builder, snapshots)
        snapshot_list = SnapshotListEnd(builder)

        builder.Finish(snapshot_list)
        return builder.Output()

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to convert JSON to FlatBuffer: {e}")
        logger.debug(f"Raw JSON data: {json_data[:1000]}...")  # Log first 1000 characters
        raise


kafka_brokers = '31.220.102.46:29092,31.220.102.46:29094'


def consume_messages():
    consumer = Consumer({
        'bootstrap.servers': kafka_brokers,
        'group.id': 'test_group',
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe(['snapshots'])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(f"Error consuming message: {msg.error()}")
                    break

            json_message = msg.value().decode('utf-8')
            logger.info(f"Received JSON message from Kafka: (size {len(json_message)})")
            logger.info(f"Received JSON message from Kafka: {json_message}")

            try:
                flatbuffer_message = json_to_flatbuffer(json_message)
                logger.info(f"Converted JSON to FlatBuffer (size {len(flatbuffer_message)})")

                # Here you can add any additional processing of the FlatBuffer message

            except json.JSONDecodeError:
                logger.warning("Received incomplete JSON message")
                logger.debug(f"Incomplete message content: {json_message}")

                # Attempt to recover partial data
                partial_data = process_incomplete_json(json_message)
                if partial_data:
                    logger.info("Processed partial data from incomplete JSON")
                    try:
                        flatbuffer_message = json_to_flatbuffer(json.dumps(partial_data))
                        logger.info(f"Converted partial JSON to FlatBuffer (size {len(flatbuffer_message)})")
                        # Process the flatbuffer_message as needed
                    except Exception as e:
                        logger.error(f"Failed to convert partial data to FlatBuffer: {e}")
                else:
                    logger.error("Unable to process the incomplete JSON message")

            except Exception as e:
                logger.error(f"Failed to process Kafka message: {e}")
                logger.debug(f"Raw message content (first 1000 chars): {json_message[:1000]}")

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping consumer.")
    finally:
        consumer.close()
        logger.info("Kafka consumer closed.")


def main():
    logger.info("Kafka Consumer Started")
    consume_messages()


if __name__ == "__main__":
    main()