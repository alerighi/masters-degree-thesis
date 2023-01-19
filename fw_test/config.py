import tomllib

from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class Config:
    mac_address: str
    aws_profile: str
    aws_region: str
    aws_iot_endpoint: str
    aws_iot_client_id: str
    wifi_interface: str
    wifi_ssid: str
    serial_port: str

    @classmethod
    def load(cls, path: str) -> Self:
        with open(path, 'rb') as f:
            config = tomllib.load(f)

        return cls(**config)
