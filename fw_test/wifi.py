import subprocess

from dataclasses import dataclass
from enum import Enum, auto
from logging import getLogger

from fw_test.config import Config

LOGGER = getLogger(__name__)

# client IP address to use
CLIENT_IP = "192.168.240.254/24"


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


def ip(args: str):
    LOGGER.debug("run: ip %s", args)
    subprocess.check_call(["ip", args.split()])


def iw(args: str):
    LOGGER.debug(f"run: iw %s", args)
    subprocess.check_call(["iw", args.split()])


def systemctl(args: str):
    LOGGER.debug(f"run: systemctl %s", args)
    subprocess.check_call(["systemctl", args.split()])


class Wifi:
    """
    handles the Wi-Fi interface of the test fixture
    """

    def __init__(self, config: Config):
        self._config = config
        self._dev = config.wifi_interface
        self._client_ssid = config.wifi_ssid

    def client_connect(self):
        """
        connect to the device AP interface
        """
        LOGGER.info("connecting to client interface")
        ip(f"addr flush dev {self._dev}")
        ip(f"route flush dev {self._dev}")
        ip(f"link set dev {self._dev} up")
        iw(f"iw dev {self._dev} disconnect")
        iw(f"iw dev {self._dev} connect {self._client_ssid}")
        ip(f"ip addr add {CLIENT_IP} dev {self._dev}")

    def client_disconnect(self):
        """
        disconnects from the device AP interface
        """
        LOGGER.info("disconnecting client interface")
        iw(f"dev {self._dev} disconnect")
        ip(f"addr flush dev {self._dev}")
        ip(f"route flush dev {self._dev}")
        ip(f"link set dev {self._dev} down")

    def start_ap(self, ap_config: ApConfiguration):
        """
        starts the host AP interface with the specified configuration
        """

        # build hostapd configuration file
        config = {
            "ssid": ap_config.ssid,
            "interface": self._config.wifi_interface,
            "driver": "nl80211",
            "hw_mode": "g",
            "channel": ap_config.channel,
            "ieee80211n": 1,
            "wmm_enabled": 0,
            # maybe in the future here we can limit to 1 specific mac address?
            "macaddr_acl": 0,
            "ignore_broadcast_ssid": 0,
            "auth_algs": 1,
        }

        if ap_config.security_type in (
            WifiSecurityType.WPA,
            WifiSecurityType.WPA2,
            WifiSecurityType.WPA3,
        ):
            if ap_config.security_type == WifiSecurityType.WPA:
                config["wpa"] = 1
            if ap_config.security_type == WifiSecurityType.WPA2:
                config["wpa"] = 2
            if ap_config.security_type == WifiSecurityType.WPA3:
                config["wpa"] = 3
            config["wpa_key_mgmt"] = "WPA - PSK"
            config["wpa_pairwise"] = "TKIP"
            config["rsn_pairwise"] = "CCMP"
            config["wpa_passphrase"] = ap_config.passphrase

        if ap_config.security_type == WifiSecurityType.WEP:
            raise NotImplementedError

        # write hostapd configuration file
        with open("/etc/hostapd/hostapd.conf", "w") as f:
            for key, value in config.items():
                print(key, "=", value, file=f)

        # start related service
        systemctl("start hostapd.service")

    def stop_ap(self):
        """
        stops the host AP interface with the specified configuration
        """
        # stop related service
        systemctl("stop hostapd.service")
