from fw_test.config import Config
from fw_test.cloud.mqtt import Mqtt
from fw_test.cloud.protocol import Protocol, Message
from fw_test.cloud.jobs import Job, JobState, AwsJobs


class Cloud:
    """
    handles the interaction with the cloud
    """

    def __init__(self, config: Config):
        self._mqtt = Mqtt(config)
        self._protocol = Protocol(config, self._mqtt)
        self._jobs = AwsJobs(config)

    def publish(self, message: Message):
        """
        publishes the specified message to the cloud.
        Handles the codification of the message into the binary
        format according to the protocol
        """
        self._protocol.publish(message)

    def receive(self) -> Message:
        """
        waits for a message incoming from the cloud, decodes
        and validates it and returns it.
        """

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


