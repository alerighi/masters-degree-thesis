import subprocess
import tempfile

from threading import Thread
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
    subprocess.check_call(["sudo", "ip"] + args.split())


def iw(args: str):
    LOGGER.debug("run: iw %s", args)
    subprocess.check_call(["sudo", "iw"] + args.split())


def systemctl(args: str):
    LOGGER.debug("run: systemctl %s", args)
    subprocess.check_call(["sudo", "systemctl"] + args.split())


def iptables(args: str):
    LOGGER.debug("run: iptables %s", args)
    subprocess.check_call(["sudo", "iptables"] + args.split())


class Wifi:
    """
    handles the Wi-Fi interface of the test fixture
    """

    def __init__(self, config: Config):
        self._config = config
        self._hostapd = None
        self._dnsmasq = None

    def client_connect(self):
        """
        connect to the device AP interface
        """
        dev = self._config.wifi_client_interface
        ssid = self._config.wifi_ssid
        LOGGER.info("connecting client interface %s to %s", dev, ssid)
        iw(f"dev {dev} set type managed")
        ip(f"addr flush dev {dev}")
        ip(f"route flush dev {dev}")
        ip(f"link set dev {dev} up")
        iw(f"dev {dev} disconnect")
        iw(f"dev {dev} connect {ssid}")
        ip(f"addr add {CLIENT_IP} dev {dev}")

    def client_disconnect(self):
        """
        disconnects from the device AP interface
        """
        dev = self._config.wifi_client_interface
        LOGGER.info("disconnecting client interface %s", dev)
        iw(f"dev {dev} disconnect")
        ip(f"addr flush dev {dev}")
        ip(f"route flush dev {dev}")
        ip(f"link set dev {dev} down")

    def start_ap(self, ap_config: ApConfiguration):
        """
        starts the host AP interface with the specified configuration
        """
        LOGGER.info("start AP with configuration %s", ap_config)

        dev = self._config.wifi_ap_interface
        ip(f"link set {dev} down")
        ip(f"addr flush dev {dev}")
        ip(f"link set {dev} up")
        ip(f"addr add 192.168.13.1/24 dev {dev}")

        LOGGER.debug("NAT traffic")
        iptables(f"-F")
        iptables(f"-t nat -F")
        iptables(f"-t nat -A POSTROUTING -o eth0 -j MASQUERADE")
        iptables(f"-A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT")
        iptables(f"-A FORWARD -i {dev} -o eth0 -j ACCEPT")

        # build hostapd configuration file
        config = {
            "interface": self._config.wifi_ap_interface,
            "ssid": ap_config.ssid,
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
            config["wpa_key_mgmt"] = "WPA-PSK"
            config["wpa_pairwise"] = "TKIP"
            config["rsn_pairwise"] = "CCMP"
            config["wpa_passphrase"] = ap_config.passphrase

        if ap_config.security_type == WifiSecurityType.WEP:
            raise NotImplementedError

        LOGGER.debug("generated hostapd config: %s", config)

        self._dnsmasq = Dnsmasq()
        self._dnsmasq.start()
        self._hostapd = Hostapd(config)
        self._hostapd.start()

    def stop_ap(self):
        """
        stops the host AP interface with the specified configuration
        """
        LOGGER.debug("stop hostapd")
        if self._hostapd:
            self._hostapd.stop()
            self._hostapd = None
        LOGGER.debug("stop dnsmasq")
        if self._dnsmasq:
            self._dnsmasq.stop()
            self._dnsmasq = None
        LOGGER.debug("all stopped")


class Hostapd:
    def __init__(self, config: dict):
        self._config = config
        self._process = None

    def start(self):
        LOGGER.debug("start hostapd")
        Thread(target=self._thread_entry, daemon=True).start()

    def stop(self):
        LOGGER.debug("stop hostapd")
        subprocess.check_call(["sudo", "killall", "hostapd"])

    def _thread_entry(self):
        config_content = ""
        for key, value in self._config.items():
            config_content += f"{key}={value}\n"

        LOGGER.debug("run hostapd with configuration: %s", config_content)

        with tempfile.NamedTemporaryFile("w") as hostapd_config:
            print(config_content, file=hostapd_config, flush=True)

            LOGGER.info("start hostapd")
            self._process = subprocess.Popen(
                    ["sudo", "hostapd", "-dd", hostapd_config.name],
                    stderr=subprocess.STDOUT,
                    stdout=subprocess.PIPE,
                    encoding="utf-8")
            for line in self._process.stdout:
                LOGGER.debug("hostapd: %s", line.strip())

            LOGGER.debug("process terminated")
            self._process = None


class Dnsmasq:
    def __init__(self):
        self._process = None

    def start(self):
        LOGGER.debug("start dnsmasq")
        Thread(target=self._thread_entry, daemon=True).start()

    def stop(self):
        LOGGER.debug("stop dnsmasq")
        subprocess.check_call(["sudo", "killall", "dnsmasq"])

    def _thread_entry(self):
        self._process = subprocess.Popen(
            ["sudo", "dnsmasq", "-d"],
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            encoding="utf-8")

        for line in self._process.stdout:
            LOGGER.debug(line.strip())

        LOGGER.debug("process terminated")
        self._process = None
