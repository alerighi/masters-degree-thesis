from enum import Enum, auto

from .config import Config


class IOValue(Enum):
    LOW = 0
    HIGH = 1


class IOPin(Enum):
    LED_R = auto()
    LED_G = auto()
    LED_B = auto()
    RELAY = auto()
    TRIAC = auto()
    BUTTON_PLUS = auto()
    BUTTON_MINUS = auto()
    FIL_PILOTE_P = auto()
    FIL_PILOTE_N = auto()
    BUZZER = auto()


class IO:
    """
    handles the interaction with the embedded device inputs/outputs
    """

    def __init__(self, config: Config):
        self._config = config

    def reset(self):
        """
        reboots the device by controlling the RESET signal
        """

    def flash_firmware(self, firmware: bytes):
        """
        flashes the specified firmware binary to the device
        """

    def read(self, pin: IOPin) -> IOValue:
        """
        reads the current value for a pin
        """

    def write(self, pin: IOPin, value: IOValue):
        """
        sets the value for a pin
        """

