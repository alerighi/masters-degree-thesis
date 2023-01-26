from queue import Queue
from logging import getLogger

from fw_test.config import Config
from fw_test.cloud.mqtt import Mqtt
from fw_test.cloud.protocol import Protocol, Message
from fw_test.cloud.jobs import Job, JobState, AwsJobs

LOGGER = getLogger(__name__)


class Cloud:
    """
    handles the interaction with the cloud
    """

    def __init__(self, config: Config):
        self._mqtt = Mqtt(config)
        self._queue = Queue()
        self._protocol = Protocol(config, self._mqtt, self._queue.put)
        self._jobs = AwsJobs(config)

    def flush(self):
        """
        remove messages that are waiting in the receive buffer
        """
        while not self._queue.empty():
            self._queue.get()

    def publish(self, message: Message):
        """
        publishes the specified message to the cloud.
        Handles the codification of the message into the binary
        format according to the protocol
        """
        self._protocol.publish(message)

    def receive(self, timeout=10) -> Message:
        """
        waits for a message incoming from the cloud, decodes
        and validates it and returns it.
        """
        return self._queue.get(block=True, timeout=timeout)

    def job_create(self, job_document: dict) -> Job:
        """
        creates an AWS job from the specified job document
        """
        return self._jobs.create(job_document)

    def job_state(self, job: Job) -> JobState:
        """
        queries the status of an AWS job
        """
        return self._jobs.state(job)

    def job_delete(self, job: Job):
        """
        deletes a created AWS job
        """
        self._jobs.delete(job)

    def stop(self):
        LOGGER.debug("cloud close")
        self._mqtt.stop()
        LOGGER.debug("cloud close ok")

    
