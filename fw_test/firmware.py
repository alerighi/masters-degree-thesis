import re
import hashlib

from logging import getLogger
from dataclasses import dataclass
from typing import Self, Optional

LOGGER = getLogger(__name__)
FW_VERSION_RE = re.compile(br"\$\$FIRMWARE_VERSION=([0-9]+)\.([0-9]+)-([a-z0-9]+)\#")
FW_VERSION_RE_STR = re.compile(r"([0-9]+)\.([0-9]+)-([a-z0-9]+)")


@dataclass(frozen=True)
class FirmwareVersion:
    major: int
    minor: int
    commit: Optional[str]

    def __str__(self):
        return f"v{self.major}.{self.minor}-{self.commit}"

    @classmethod
    def from_bytes(cls, version: bytes) -> Self:
        if len(version) != 2:
            raise ValueError("firmware version must be a 2 byte array")

        return cls(major=version[0], minor=version[1], commit=None)

    @classmethod
    def from_str(cls, version: str) -> Self:
        major, minor, commit = FW_VERSION_RE_STR.search(version).groups()

        return cls(major=int(major), minor=int(minor), commit=commit)


@dataclass(frozen=True)
class Firmware:
    """
    represents the firmware of a device
    """
    version: FirmwareVersion
    binary: bytes
    hash: str

    @classmethod
    def load_file(cls, path: str) -> Self:
        """
        load a firmware from a file
        """
        LOGGER.info("loading firmware from %s", path)

        with open(path, "rb") as f:
            binary = f.read()

        major, minor, commit = FW_VERSION_RE.search(binary).groups()

        return cls(
            binary=binary, 
            hash=hashlib.sha256(binary).hexdigest(),
            version=FirmwareVersion(int(major), int(minor), commit.decode('ascii'))
        )
