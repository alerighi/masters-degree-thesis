from time import time

import requests

from fw_test.context import Context
from fw_test.io import IOPin, IOValue
from fw_test.wifi import ApConfiguration, WifiSecurityType
from fw_test.cloud import Message, Action, Response, PacketType

from .utils import assert_status_led_color, LedColor

TEST_SSID = "TEST-NETWORK"
TEST_PASSPHRASE = "test-network-passphrase"


def test_pairing(ctx: Context):
    # check that the LED is fixed RED
    assert_status_led_color(ctx, LedColor.RED)

    # check that the relay is OFF
    assert ctx.io.read(IOPin.RELAY) == IOValue.LOW
    assert ctx.io.read(IOPin.TRIAC) == IOValue.LOW

    # connect to the device Wi-Fi AP
    ctx.wifi.client_connect()

    # send the provisioning request
    req = requests.post("http://192.168.240.1/irsap/provision", json={
        "ssid": TEST_SSID,
        "security": "wpa",
        "passphrase": TEST_PASSPHRASE,
        "env_id": "random uuid here...",
    })
    assert req.status_code == 200

    # activate the device software AP
    ctx.wifi.start_ap(ApConfiguration(
        ssid=TEST_SSID,
        passphrase=TEST_PASSPHRASE,
        security_type=WifiSecurityType.WPA2,
        channel=6,
    ))

    # wait for the connection of the device to the cloud
    msg = ctx.cloud.receive()
    assert msg.action == Action.GET

    # send a GET rejected to the device (we don't have current state)
    ctx.cloud.publish(Message(
        action=Action.GET,
        response=Response.REJECTED,
        state={
            "clientToken": int(time()),
            "timestamp": int(time()),
            "requestId": 0,
            "type": PacketType.HEADER,
        }
    ))  # todo

    # the device should respond with its state with a version of 0
    msg = ctx.cloud.receive()
    assert msg.method == Action.REPORTED_UPDATE
    assert msg.state["version"] == 0
