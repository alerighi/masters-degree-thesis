from queue import Queue
from logging import getLogger
from time import time
from uuid import uuid4
from typing import Optional

from boto3 import Session

from fw_test.config import Config
from fw_test.cloud.mqtt import Mqtt
from fw_test.cloud.protocol import Protocol, Message, Action
from fw_test.cloud.state import PacketType
from fw_test.cloud.jobs import Job, JobState, AwsJobs
from fw_test.firmware import Firmware

LOGGER = getLogger(__name__)


class Cloud:
    """
    handles the interaction with the cloud
    """

    def __init__(self, config: Config):
        session = Session(
            profile_name=config.aws_profile,
            region_name=config.aws_region,
        )
        self._config = config
        self._mqtt = Mqtt(config)
        self._queue = Queue()
        self._protocol = Protocol(config, self._mqtt, self._queue.put)
        self._jobs = AwsJobs(config, session.client("iot"))
        self._s3 = session.client("s3")

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

    def receive(self, timeout=10, ignore_connection=True, filter_action: Optional[Action] = None) -> Message:
        """
        waits for a message incoming from the cloud, decodes
        and validates it and returns it.
        """
        packet = self._queue.get(block=True, timeout=timeout)
        start = time()
        if (filter_action is not None and packet.action != filter_action) \
                or (ignore_connection and packet.action == Action.REPORTED_UPDATE and packet.state["type"] == PacketType.CONNECTION.value):
            LOGGER.debug("received ingored packet, ignore...")
            return self.receive(timeout=timeout - (time() - start), ignore_connection=True, filter_action=filter_action)

        return packet

    def job_create(self, job: Job):
        """
        creates an AWS job from the specified job document
        """
        self._jobs.create(job)

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

    def send_ota(self, firmware: Firmware) -> Job: 
        """
        sends an OTA update to the device
        """
        LOGGER.info("sending an OTA update with version %s", firmware.version)

        s3_path = f"firmware/RE/{firmware.hash[-8:]}-{firmware.version.commit}"
        
        LOGGER.debug("upload file to s3")
        self._s3.put_object(
            ACL='public-read',
            Body=firmware.binary,
            Bucket=self._config.ota_bucket,
            Key=s3_path,
        )

        url = f"http://reota.irsap.cloud/{self._config.ota_bucket}/{s3_path}"
        job_id = f"RE-{firmware.version}-{str(uuid4())}".replace('.', '-')
        job_document = {
            'operation': "fwInstall",
            'files': {
                'name': job_id,
                'version': f"{firmware.version.major}.{firmware.version.minor}",
                'url': url,
                'codesign': firmware.hash,
            }
        }
        job = Job(job_id, job_document)

        self.job_create(job)

        return job

    def stop(self):
        LOGGER.debug("cloud close")
        self._mqtt.stop()
        LOGGER.debug("cloud close ok")

    
