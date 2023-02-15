from enum import Enum

from fw_test.cloud.serializer import serialize, deserialize, sizeof

PACKET_HEADER = {
    "clientToken": "u32",
    "timestamp": "u32",
    "version": "u32",
    "length": "u16",
    "type": "u8"
}

PACKET_CONNECTION = {
    **PACKET_HEADER,
    "connected": "u8"
}

PACKET_BODY_RW_V1 = {
    "systemConfiguration": "u8",
    "metricInterval": "u16",
    "powerConfig": "u8",
    "openWindowOffTimeMinutes": "u8",
    "setPointOff": "i16",
    "setPointEco": "u8",
    "manualSetPoint": "u8",
    "temporaryManualSetPoint": "u8",
    "boostDuration": "u8",
    "hysteresis": "u8",
    "temperatureSensorOffset": "i8",
    "ledStatus": "u32",
    "envId": "u8[16]",
    "ipAddress": "u8[4]",
    "temporaryManualEnd": "u32",
    "holidayStart": "u32",
    "holidayEnd": "u32",
    "timezone": "i16",
    "schedule": "u8[154]",
}

PACKET_BODY_R_V1 = {
    "connected": "u8",
    "firmwareVersion": "u8[2]",
    "hardwareVersion": "u8",
    "macAddress": "u8[6]",
    "systemStatus": "u8",
    "filPiloteStatus": "u8",
    "alarm": "u8",
    "heatingStatus": "u8",
    "signalQuality": "u8[2]",
    "loadOnSeconds": "u32",
    "currentSetPointEnd": "u32",
    "currentSetPoint": "i16",
    "co2Value": "u16",
    "vocValue": "u16",
    "temperature": "i16",
    "loadTemperature": "i16",
}

PACKET_STATE_DESIRED_V1 = {
    **PACKET_HEADER,
    **PACKET_BODY_RW_V1,
}

PACKET_STATE_REPORTED_V1 = {
    **PACKET_STATE_DESIRED_V1,
    **PACKET_BODY_R_V1,
}

PACKET_BODY_RW_V2 = {
    "ledEnable": "u8",
    "ledMode": "u8",
    "ledSchedule": "u8[154]",
    "ledColors": "u8[40]",
    "temporaryManualLedSetPoint": "u32",
    "temporaryManualLedSetPointEnd": "u32",
    "estimatedTemperature": "i16",
    "externalTemperature": "i16",
    "estimatedHumidity": "u8",
    "externalHumidity": "u8",
    "timesyncServer": "u8[32]",
    "forFutureUsage_rw": "u8[68]",
}

PACKET_BODY_R_V2 = {
    "currentLedSetPoint": "u32",
    "currentLedSetPointEnd": "u32",
    "cartridgePowerWatts": "u16",
    "cumulatedConsumptionWattHour": "u32",
    "cumulatedConsumptionWattHourSnapshotValue": "u32",
    "cumulatedConsumptionWattHourSnapshotTime": "u32",
    "modelName": "u8[20]",
    "forFutureUsage_r": "u8[100]",
}

PACKET_STATE_DESIRED_V2 = {
    **PACKET_HEADER,
    **PACKET_BODY_RW_V1,
    **PACKET_BODY_RW_V2,
}

PACKET_STATE_REPORTED_V2 = {
    **PACKET_HEADER,
    **PACKET_BODY_RW_V1,
    **PACKET_BODY_RW_V2,
    **PACKET_BODY_R_V1,
    **PACKET_BODY_R_V2,
}


class PacketType(Enum):
    HEADER = 0
    STATE_REPORTED_V1 = 1
    STATE_DESIRED_V1 = 2
    CONNECTION = 3
    STATE_REPORTED_V2 = 4
    STATE_DESIRED_V2 = 5


STRUCTURE = {
    PacketType.HEADER.value: PACKET_HEADER,
    PacketType.CONNECTION.value: PACKET_CONNECTION,
    PacketType.STATE_DESIRED_V1.value: PACKET_STATE_DESIRED_V1,
    PacketType.STATE_DESIRED_V2.value: PACKET_STATE_DESIRED_V2,
    PacketType.STATE_REPORTED_V1.value: PACKET_STATE_REPORTED_V1,
    PacketType.STATE_REPORTED_V2.value: PACKET_STATE_REPORTED_V2,
}

SYSTEM_STATUS_WORKING = 0x01
SYSTEM_STATUS_HEATING = 0x02
SYSTEM_STATUS_LOAD_ACTIVE = 0x08

def to_binary(state: dict) -> bytes:
    if isinstance(state["type"], PacketType):
        state["type"] = state["type"].value

    structure = STRUCTURE[state["type"]]

    # compute length so that it can be not specified when encoding
    state["length"] = sizeof(structure)

    return serialize(structure, state)


def from_binary(binary: bytes) -> dict:
    # deserialize only header to know packet type
    header_size = sizeof(PACKET_HEADER)
    header = deserialize(PACKET_HEADER, binary[:header_size])

    # now I can get the appropriate deserializer for this packet
    structure = STRUCTURE[header["type"]]

    return deserialize(structure, binary)
