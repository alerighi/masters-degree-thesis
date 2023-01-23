from logging import getLogger
from typing import Callable

from awscrt.auth import AwsCredentialsProvider
from awscrt.mqtt import QoS
from awscrt.io import EventLoopGroup, DefaultHostResolver, ClientBootstrap
from awsiot import mqtt_connection_builder

from fw_test.config import Config

LOGGER = getLogger(__name__)


class Mqtt:
    """
    handles the MQTT communication with the server
    """

    def __init__(self, config: Config):
        event_loop_group = EventLoopGroup(1)
        host_resolver = DefaultHostResolver(event_loop_group)
        client_bootstrap = ClientBootstrap(event_loop_group, host_resolver)
        credentials_provider = AwsCredentialsProvider.new_profile(profile_name=config.aws_profile)
        self._connection = mqtt_connection_builder.websockets_with_default_aws_signing(
            endpoint=config.aws_iot_endpoint,
            region=config.aws_region,
            credentials_provider=credentials_provider,
            client_bootstrap=client_bootstrap,
            client_id=config.aws_iot_client_id,
            clean_session=True,
            keep_alive_secs=20,
        )

        LOGGER.info("connecting to AWS IoT Core")
        self._connection.connect().result(timeout=5)

        LOGGER.debug("connected to AWS IoT Core")

    def publish(self, topic: str, message: bytes):
        """
        publishes a message to a topic
        """

        LOGGER.info("publish on %s message of %s bytes", topic, len(message))
        future, packet_id = self._connection.publish(topic, payload=message, qos=QoS.AT_LEAST_ONCE)

        LOGGER.debug("packet id=%s", packet_id)
        future.result(timeout=5)

        LOGGER.debug("publish on topic %s success", topic)

    def subscribe(self, topic_filter: str, callback: Callable[[str, bytes], None]):
        """
        subscribes to the specified topic filter
        """

        LOGGER.info("subscribing to topic filter %s")
        future, packet_id = self._connection.subscribe(topic_filter, qos=QoS.AT_LEAST_ONCE, callback=callback)

        LOGGER.debug("subscribe packet id is %s", packet_id)
        future.result(timeout=5)

        LOGGER.debug("subscribe on topic filter %s success", topic_filter)

