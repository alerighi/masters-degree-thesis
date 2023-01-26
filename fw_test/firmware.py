import re

from logging import getLogger
from dataclasses import dataclass
from typing import Self

LOGGER = getLogger(__name__)
FW_VERSION_RE = re.compile(br"\$\$FIRMWARE_VERSION=([0-9]+)\.([0-9]+)-([a-z0-9]+)\#")


@dataclass(frozen=True)
class FirmwareVersion:
    major: int
    minor: int
    commit: str

    def __str__(self):
        return f"v{self.major}.{self.minor}-{self.commit}"


@dataclass(frozen=True)
class Firmware:
    """
    represents the firmware of a device
    """
    version: FirmwareVersion
    binary: bytes

    @classmethod
    def load_file(cls, path: str) -> Self:
        """
        load a firmware from a file
        """
        LOGGER.info("loading firmware from %s", path)

        with open(path, "rb") as f:
            binary = f.read()

        major, minor, commit = FW_VERSION_RE.search(binary).groups()

        return cls(binary=binary, version=FirmwareVersion(int(major), int(minor), commit.decode('ascii')))

