from enum import Enum
from time import sleep

import requests

from fw_test.context import Context
from fw_test.io import IOPin, IOValue
from fw_test.wifi import ApConfiguration, WifiSecurityType
from fw_test.cloud import Message
from fw_test.firmware import FirmwareVersion


class LedColor(Enum):
    OFF = (0, 0, 0)
    RED = (1, 0, 0)
    GREEN = (0, 1, 0)
    BLUE = (0, 0, 1)
    YELLOW = (1, 1, 0)
    CYAN = (0, 1, 1)
    MAGENTA = (1, 0, 1)
    WHITE = (1, 1, 1)


WIFI_SECURITY_MAP_TO_RE = {
    WifiSecurityType.NONE: "none",
    WifiSecurityType.WEP: "wep",
    WifiSecurityType.WPA: "wpa",
    WifiSecurityType.WPA2: "wpa",
    WifiSecurityType.WPA3: "wpa",
}


def assert_status_led_color(ctx: Context, color: LedColor):
    """
    checks that the status LED is of the specified color
    """

    r, g, b = color.value

    assert ctx.io.read(IOPin.LED_R) == IOValue.HIGH if r else IOValue.LOW
    assert ctx.io.read(IOPin.LED_G) == IOValue.HIGH if g else IOValue.LOW
    assert ctx.io.read(IOPin.LED_B) == IOValue.HIGH if b else IOValue.LOW


def assert_load_state(ctx: Context, active: bool):
    # triac should be normally off (not that it's an active-low signal)
    assert ctx.io.read(IOPin.TRIAC) == IOValue.HIGH

    # relay should reflect the state of the load
    assert ctx.io.read(IOPin.RELAY) == IOValue.HIGH if active else IOValue.LOW


def assert_provision_ok(ap_configuration: ApConfiguration, env_id: str):
    req = requests.post("http://192.168.240.1/irsap/provision", json={
        "ssid": ap_configuration.ssid,
        "security": WIFI_SECURITY_MAP_TO_RE[ap_configuration.security_type],
        "passphrase": ap_configuration.passphrase,
        "envId": env_id,
    }, timeout=5)
    assert req.status_code == 200


def assert_firmware_version(msg: Message, version: FirmwareVersion):
    major, minor = msg.state["firmwareVersion"]

    assert version.major == major
    assert version.minor == minor


def hard_reset_procedure(ctx: Context):
    # press + and - for at least 8 seconds
    ctx.io.write(IOPin.BUTTON_MINUS, IOValue.LOW)
    ctx.io.write(IOPin.BUTTON_PLUS, IOValue.LOW)

    sleep(8)

    ctx.io.write(IOPin.BUTTON_MINUS, IOValue.HIGH)
    ctx.io.write(IOPin.BUTTON_PLUS, IOValue.HIGH)

    # now LED should be YELLOW
    assert_status_led_color(ctx, LedColor.YELLOW)

    # press one button
    ctx.io.write(IOPin.BUTTON_MINUS, IOValue.LOW)

    sleep(0.2)

    ctx.io.write(IOPin.BUTTON_MINUS, IOValue.HIGH)

    # wait for 5 seconds for the device to reboot 
    sleep(5)

    assert_status_led_color(ctx, LedColor.RED)

