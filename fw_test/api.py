import requests

from uuid import UUID
from logging import getLogger

from fw_test.wifi import WifiSecurityType, ApConfiguration
from fw_test.firmware import Firmware
from fw_test.config import Config

LOGGER = getLogger(__name__)
REQUEST_TIMEOUT = 5
FWUPDATE_TIMEOUT = 30

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

    def provision(self, ap_configuration: ApConfiguration, env_id: UUID) -> dict:
        """
        send a provisioning request to the RE device
        """
        payload_json = {
            "ssid": ap_configuration.ssid,
            "security": WIFI_SECURITY_MAP_TO_RE[ap_configuration.security_type],
            "passphrase": ap_configuration.passphrase,
            "envId": str(env_id),
        }
        LOGGER.info("provision the RE with %s", payload_json)

        response = requests.post(BASE_URL + "/irsap/provision", json=payload_json, timeout=REQUEST_TIMEOUT).json()

        LOGGER.info("provision response: %s", response)

        return response

    def wifi_scan(self) -> list:
        """
        return the list of network scanned by the RE device
        """
        LOGGER.info("ask the RE to scan Wi-Fi networks")

        response =  requests.get(BASE_URL + "/irsap/wifi/scan", timeout=REQUEST_TIMEOUT).json()

        LOGGER.info("scan result: %s", response)

        return response

    def status(self) -> dict:
        """
        gets the status of the RE device
        """
        LOGGER.info("ask status to the RE")

        response = requests.get(BASE_URL + "/irsap/state", timeout=REQUEST_TIMEOUT).json()

        LOGGER.info("status response: %s", response)

        return response

    def firmware_update(self, firmware: Firmware) -> requests.Response:
        """
        upgrade the firmware of the RE device
        """
        LOGGER.info("send firmware update version %s", firmware.version)

        response = requests.post(BASE_URL + "/gainspan/system/fwuploc", files={ "fw_image": firmware.binary }, timeout=FWUPDATE_TIMEOUT)

        LOGGER.info("fwup response: %s %s", response.status_code, response.text)

        return response

