from fw_test.cloud import PacketType
from fw_test.wifi import ApConfiguration, WifiSecurityType

STATE_MANUAL = {
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

TEST_SSID = "TEST-NETWORK"
TEST_PASSPHRASE = "test-network-passphrase"

TEST_AP_CONFIG = ApConfiguration(
    ssid=TEST_SSID,
    passphrase=TEST_PASSPHRASE,
    security_type=WifiSecurityType.WPA2,
    channel=6,
)
