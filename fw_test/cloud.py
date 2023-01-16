from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from .config import Config


class Method(Enum):
    GET = auto()
    PUT = auto()
    DELETE = auto()


@dataclass
class Message:
    method: Method
    version: int
    timestamp: int
    body: dict[str, Any]


class JobState(Enum):
    QUEUED = auto()
    IN_PROGRESS = auto()
    SUCCESS = auto()
    FAILURE = auto()
    TIMEOUT = auto()


@dataclass
class Job:
    pass


class Cloud:
    """
    handles the interaction with the cloud
    """

    def __init__(self, config: Config):
        self._config = config

    def publish(self, message: Message):
        """
        publishes the specified message to the cloud.
        Handles the codification of the message into the binary
        format according to the protocol
        """
        pass

    def receive(self) -> Message:
        """
        waits for a message incoming from the cloud, decodes
        and validates it and returns it.
        """

    def job_create(self, job_document: dict) -> Job:
        """
        creates an AWS job from the specified job document
        """

    def job_state(self, job: Job) -> JobState:
        """
        queries the status of an AWS job
        """

    def job_delete(self, job: Job):
        """
        deletes a created AWS job
        """


