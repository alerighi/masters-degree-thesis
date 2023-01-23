from logging import getLogger
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Tuple, Callable

from fw_test.cloud.mqtt import Mqtt
from fw_test.config import Config
from fw_test.cloud.state import from_binary, to_binary

LOGGER = getLogger(__name__)


class Action(Enum):
    GET = auto()
    DESIRED_UPDATE = auto()
    REPORTED_UPDATE = auto()
    DELETE = auto()


TOPIC_ACTION = {
    Action.GET: "get",
    Action.DESIRED_UPDATE: "desired-update",
    Action.REPORTED_UPDATE: "reported-update",
    Action.DELETE: "delete",
}


class Response(Enum):
    ACCEPTED = auto()
    REJECTED = auto()


TOPIC_RESPONSE = {
    Response.ACCEPTED: "accepted",
    Response.REJECTED: "rejected",
}


@dataclass
class Message:
    action: Action
    response: Optional[Response]
    state: dict


class Protocol:
    """
    class that implements the device/cloud protocol
    """

    def __init__(self, config: Config, mqtt: Mqtt, callback: Callable[[Message], None]):
        self._mqtt = mqtt
        self._topic_base = f"re/things/{config.mac_address}/shadow"

        # start required subscription
        self._mqtt.subscribe(f"{self._topic_base}/#", self._on_message)
        self._callback = callback

    def publish(self, message: Message):
        topic = self._topic_for(message)
        payload = to_binary(message.state)

        self._mqtt.publish(topic, payload)

    def _on_message(self, topic: str, payload: bytes):
        LOGGER.info("received message on topic %s", topic)

        action, response = self._topic_parse(topic)
        state = from_binary(payload)
        message = Message(action, response, state)

        LOGGER.debug("decoded message: %s", message)
        self._callback(message)

    def _topic_for(self, message: Message) -> str:
        parts = [self._topic_base, TOPIC_ACTION[message.action]]

        if message.response:
            parts.append(TOPIC_RESPONSE[message.response])

        return "/".join(parts)

    def _topic_parse(self, topic: str) -> Tuple[Action, Optional[Response]]:
        parts = topic.removeprefix(self._topic_base).split("/")[1:]

        action = next(action for action, topic in TOPIC_ACTION.items() if topic == parts[0])
        response = None
        if len(parts) > 1:
            response = next(response for response, topic in TOPIC_RESPONSE.items() if topic == parts[1])

        return action, response
