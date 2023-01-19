from enum import Enum
from time import sleep
from logging import getLogger

from RPi import GPIO
from serial import Serial

from fw_test.config import Config

LOGGER = getLogger(__name__)
CONSOLE_BAUDRATE = 115200


class IOValue(Enum):
    LOW = GPIO.LOW
    HIGH = GPIO.HIGH


# Pin assignment
#                                         Pin 1 Pin2
#                                      +3V3 [ ] [ ] +5V
#                            SDA1 / GPIO  2 [ ] [ ] +5V
#                            SCL1 / GPIO  3 [ ] [ ] GND
#                           (RESET) GPIO  4 [ ] [ ] GPIO 14 / TXD0
#                                       GND [ ] [ ] GPIO 15 / RXD0
#                                   GPIO 17 [ ] [ ] GPIO 18
#                          (BUZZER) GPIO 27 [ ] [ ] GND
#                           (LED_R) GPIO 22 [ ] [ ] GPIO 23 (LED_G)
#                                      +3V3 [ ] [ ] GPIO 24 (LED_B)
#             (FIL_PILOTE_N) MOSI / GPIO 10 [ ] [ ] GND
#             (FIL_PILOTE_P) MISO / GPIO  9 [ ] [ ] GPIO 25 (RELAY)
#         (CURRENT_FEEDBACK) SCLK / GPIO 11 [ ] [ ] GPIO  8 / CE0# (BUTTON_MINUS)
#                                       GND [ ] [ ] GPIO  7 / CE1# (BUTTON_PLUS)
#                           ID_SD / GPIO  0 [ ] [ ] GPIO  1 / ID_SC
#                            (BOOT) GPIO  5 [ ] [ ] GND
#                         (RESTORE) GPIO  6 [ ] [ ] GPIO 12
#                                   GPIO 13 [ ] [ ] GND
#                            MISO / GPIO 19 [ ] [ ] GPIO 16 / CE2#
#                           (TRIAC) GPIO 26 [ ] [ ] GPIO 20 / MOSI
#                                       GND [ ] [ ] GPIO 21 / SCLK
#                                       Pin 39 Pin 40
class IOPin(Enum):
    # outputs
    RESET = 4
    BOOT = 5
    RESTORE = 6
    BUTTON_PLUS = 7
    BUTTON_MINUS = 8
    FIL_PILOTE_P = 9
    FIL_PILOTE_N = 10
    CURRENT_FEEDBACK = 11

    # inputs
    LED_R = 22
    LED_G = 23
    LED_B = 24
    RELAY = 25
    TRIAC = 26
    BUZZER = 27


class IO:

    """
    handles the interaction with the embedded device inputs/outputs
    """

    def __init__(self, config: Config):
        self._config = config
        self._serial = Serial(port=config.serial_port, baudrate=CONSOLE_BAUDRATE)
        self._serial.open()

        GPIO.setmode(GPIO.BOARD)

        def setup(pin: IOPin, mode: int):
            LOGGER.debug("setup pin %s (%s) as %s", pin.name, pin.value, "INPUT" if mode == GPIO.IN else "OUTPUT")
            GPIO.setup(pin.value, mode)

        # setup all inputs
        setup(IOPin.LED_R, GPIO.IN)
        setup(IOPin.LED_G, GPIO.IN)
        setup(IOPin.LED_B, GPIO.IN)
        setup(IOPin.TRIAC, GPIO.IN)
        setup(IOPin.RELAY, GPIO.IN)
        setup(IOPin.BUZZER, GPIO.IN)

        # setup all outputs
        setup(IOPin.RESET, GPIO.OUT)
        setup(IOPin.BOOT, GPIO.OUT)
        setup(IOPin.BUTTON_PLUS, GPIO.OUT)
        setup(IOPin.BUTTON_MINUS, GPIO.OUT)
        setup(IOPin.FIL_PILOTE_P, GPIO.OUT)
        setup(IOPin.FIL_PILOTE_N, GPIO.OUT)
        setup(IOPin.CURRENT_FEEDBACK, GPIO.OUT)

    def reset(self):
        """
        reboots the device by controlling the RESET signal
        """
        LOGGER.info("reset board")
        self.write(IOPin.RESET, GPIO.LOW)

        sleep(0.1)

        self.write(IOPin.BOOT, GPIO.LOW)
        self.write(IOPin.RESTORE, GPIO.LOW)
        self.write(IOPin.RESET, GPIO.HIGH)

    def flash_firmware(self, firmware: bytes):
        """
        flashes the specified firmware binary to the device
        """
        raise NotImplementedError

    def restore_firmware(self):
        """
        restores the board with the factory (under test) firmware
        """
        LOGGER.info("restore board firmware")

        self.write(IOPin.RESET, GPIO.LOW)
        self.write(IOPin.RESTORE, GPIO.HIGH)
        self.write(IOPin.BOOT, GPIO.HIGH)

        sleep(0.1)
        self.write(IOPin.RESET, GPIO.HIGH)

        sleep(0.1)
        self.reset()

    def read(self, pin: IOPin) -> IOValue:
        """
        reads the current value for a pin
        """
        return IOValue(GPIO.input(pin.value))

    def write(self, pin: IOPin, value: IOValue):
        """
        sets the value for a pin
        """
        LOGGER.debug("set pin %s %s", pin.name, value.name)
        GPIO.output(pin.value, value.value)

    def serial_readline(self) -> str:
        """
        reads one line of text form the debug serial port
        """
        return self._serial.readline().decode("ascii")

    def serial_write(self, data: str):
        """
        writes data to the serial port
        """
        self._serial.write(data.encode("ascii"))

