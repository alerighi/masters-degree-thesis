from dataclasses import dataclass
from enum import Enum, auto

from .config import Config


class WifiSecurityType(Enum):
    NONE = auto()
    WEP = auto()
    WPA = auto()
    WPA2 = auto()
    WPA3 = auto()


@dataclass(frozen=True)
class ApConfiguration:
    ssid: str
    security_type: WifiSecurityType
    passphrase: str
    channel: int


class Wifi:
    """
    handles the Wi-Fi interface of the test fixture
    """

    def __init__(self, config: Config):
        self._config = config

    def client_connect(self):
        """
        connect to the device AP interface
        """
        pass

    def client_disconnect(self):
        """
        disconnects from the device AP interface
        """
        pass

    def start_ap(self, ap_config: ApConfiguration):
        """
        starts the host AP interface with the specified configuration
        """
        pass

    def stop_ap(self):
        """
        stops the host AP interface with the specified configuration
        """
        pass
