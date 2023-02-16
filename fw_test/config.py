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
    wifi_ap_interface: str
    wifi_client_interface: str
    wifi_ssid: str
    serial_port: str
    prev_firmware_path: str
    ota_bucket: str

    @classmethod
    def load_file(cls, path: str) -> Self:
        with open(path, "rb") as f:
            config = tomllib.load(f)

        return cls(**config)
