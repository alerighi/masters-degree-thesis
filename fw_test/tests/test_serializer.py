import pytest

from fw_test.cloud.serializer import to_struct_fmt, sizeof
from fw_test.cloud import state
from fw_test.cloud import PacketType

def test_to_struct_fmt():
    assert to_struct_fmt("u8") == "B"
    assert to_struct_fmt("i8") == "b"
    assert to_struct_fmt("u16") == "H"
    assert to_struct_fmt("i16") == "h"
    assert to_struct_fmt("u32") == "L"
    assert to_struct_fmt("i32") == "l"
    assert to_struct_fmt("u8[9]") == "9s"
    assert to_struct_fmt("u8[99]") == "99s"

    with pytest.raises(RuntimeError):
        to_struct_fmt("u16[1]")


def test_sizeof_calculation():
    assert sizeof({ "test": "u8[8]" }) == 8
    assert sizeof({ "test": "u8" }) == 1
    assert sizeof({ "test": "i8" }) == 1
    assert sizeof({ "test": "u16" }) == 2
    assert sizeof({ "test": "i16" }) == 2
    assert sizeof({ "test": "i32" }) == 4
    assert sizeof({ "test": "i32" }) == 4


def test_sizeof_state():
    assert sizeof(state.PACKET_HEADER) == 15
    assert sizeof(state.PACKET_BODY_R_V1) == 34
    assert sizeof(state.PACKET_BODY_RW_V1) == 205
    assert sizeof(state.PACKET_BODY_R_V2) == 142
    assert sizeof(state.PACKET_BODY_RW_V2) == 310
    assert sizeof(state.PACKET_STATE_DESIRED_V2) == 530
    assert sizeof(state.PACKET_STATE_REPORTED_V2) == 706


def test_encode_state():
    test_state = {
        "clientToken": 0,
        "timestamp": 0,
        "version": 0,
        "type": PacketType.STATE_DESIRED_V2.value,
        "systemConfiguration": 0,
        "metricInterval": 20,
        "powerConfig": 100,
        "openWindowOffTimeMinutes": 15,
        "setPointOff": 50,
        "setPointEco": 80,
        "manualSetPoint": 120,
        "temporaryManualSetPoint": 0,
        "boostDuration": 100,
        "hysteresis": 5,
        "temperatureSensorOffset": 0,
        "ledStatus": 0,
        "envId": b"\0" * 16,
        "temporaryManualEnd": 0,
        "holidayStart": 0,
        "holidayEnd": 0,
        "timezone": 60,
        "schedule": b"\0" * 154,
        "ledEnable": 0,
        "ledMode": 0,
        "ledSchedule": b"\0" * 154,
        "ledColors": b"\0" * 10 * 4,
        "temporaryManualLedSetPoint": 0,
        "temporaryManualLedSetPointEnd": 0,
        "estimatedTemperature": 0,
        "externalTemperature": 0,
        "estimatedHumidity": 0,
        "externalHumidity": 0,
        "timesyncServer": b"\0" * 32,
        "ipAddress": b"\0" * 4,
        "forFutureUsage_rw": b"\0" * 68
    }
    binary = state.to_binary(test_state)
    assert state.from_binary(binary) == test_state