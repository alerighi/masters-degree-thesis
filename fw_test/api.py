import requests

from uuid import UUID

from fw_test.wifi import WifiSecurityType, ApConfiguration
from fw_test.firmware import Firmware
from fw_test.config import Config

REQUEST_TIMEOUT = 5
WIFI_SECURITY_MAP_TO_RE = {
    WifiSecurityType.NONE: "none",
    WifiSecurityType.WEP: "wep",
    WifiSecurityType.WPA: "wpa",
    WifiSecurityType.WPA2: "wpa",
    WifiSecurityType.WPA3: "wpa",
}
BASE_URL = "http://192.168.240.1"


class LocalApi:
    """
    electric radiator local API for communicating with the app
    """
    def __init__(self, config: Config):
        self._config = config

    def provision(self, ap_configuration: ApConfiguration, env_id: UUID) -> requests.Response:
        """
        send a provisioning request to the RE device
        """
        return requests.post(BASE_URL + "/irsap/provision", json={
            "ssid": ap_configuration.ssid,
            "security": WIFI_SECURITY_MAP_TO_RE[ap_configuration.security_type],
            "passphrase": ap_configuration.passphrase,
            "envId": str(env_id),
        }, timeout=REQUEST_TIMEOUT)

    def wifi_scan(self):
        """
        return the list of network scanned by the RE device
        """
        return requests.get(BASE_URL + "/irsap/wifi/scan", timeout=REQUEST_TIMEOUT)

    def status(self):
        """
        gets the status of the RE device
        """

        return requests.get(BASE_URL + "/irsap/state", timeout=REQUEST_TIMEOUT)

    def firmware_update(self, firmware: Firmware):
        """
        upgrade the firmware of the RE device
        """
        return requests.post(BASE_URL + "/gainspan/system/fwuploc", data=firmware.binary)


