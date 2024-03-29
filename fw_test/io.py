from enum import Enum
from time import sleep
from logging import getLogger
from threading import Thread

from RPi import GPIO
from serial import Serial
from serial.threaded import LineReader, ReaderThread

from fw_test.config import Config
from fw_test.firmware import Firmware

LOGGER = getLogger(__name__)
CONSOLE_BAUDRATE = 115200


class SerialReader(LineReader):
    TERMINATOR = b"\n"
    ENCODING = "latin-1"

    def handle_line(self, line):
        LOGGER.debug("RE: %s", line)


class IOValue(Enum):
    LOW = GPIO.LOW
    HIGH = GPIO.HIGH

    def __int__(self):
        return 1 if self.value == IOValue.HIGH else 0


class LedColor(Enum):
    OFF = (0, 0, 0)
    RED = (1, 0, 0)
    GREEN = (0, 1, 0)
    BLUE = (0, 0, 1)
    YELLOW = (1, 1, 0)
    CYAN = (0, 1, 1)
    MAGENTA = (1, 0, 1)
    WHITE = (1, 1, 1)


BUTTON_DOWN_VALUE = IOValue.LOW
BUTTON_UP_VALUE = IOValue.HIGH

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
        self._serial = Serial(port=config.serial_port, baudrate=CONSOLE_BAUDRATE, timeout=10)
        self._reader = Thread(target=self.serial_read, daemon=True)
        self._reader = ReaderThread(self._serial, SerialReader)
        self._reader.start()

        GPIO.setmode(GPIO.BCM)
        
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
        setup(IOPin.RESTORE, GPIO.OUT)
        setup(IOPin.BUTTON_PLUS, GPIO.OUT)
        setup(IOPin.BUTTON_MINUS, GPIO.OUT)
        setup(IOPin.FIL_PILOTE_P, GPIO.OUT)
        setup(IOPin.FIL_PILOTE_N, GPIO.OUT)
        setup(IOPin.CURRENT_FEEDBACK, GPIO.OUT)

        self.write(IOPin.BUTTON_MINUS, BUTTON_UP_VALUE)
        self.write(IOPin.BUTTON_PLUS, BUTTON_UP_VALUE)

    def reset(self):
        """
        reboots the device by controlling the RESET signal
        """
        LOGGER.info("reset board")
        self.write(IOPin.RESET, IOValue.LOW)

        sleep(0.1)

        self.write(IOPin.BOOT, IOValue.LOW)
        self.write(IOPin.RESTORE, IOValue.LOW)
        self.write(IOPin.RESET, IOValue.HIGH)

    def flash_firmware(self, firmware: Firmware):
        """
        flashes the specified firmware binary to the device
        """
        raise NotImplementedError

    def restore_firmware(self):
        """
        restores the board with the factory (under test) firmware
        """
        LOGGER.info("restore board firmware")

        self.write(IOPin.RESET, IOValue.LOW)
        self.write(IOPin.RESTORE, IOValue.HIGH)

        sleep(0.1)
        self.write(IOPin.RESET, IOValue.HIGH)

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
        LOGGER.debug("set pin %s(%s) %s(%s)", pin.name, pin.value, value.name, value.value)
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

    def stop(self):
        LOGGER.debug("stop serial reader")
        self._reader.stop()

        GPIO.cleanup() 


    def serial_read(self):
        try:
            while True:
                line = self._serial.readline()
                LOGGER.debug("RE: %s", line.decode("latin-1").strip())
        except:
            LOGGER.debug("serial reader stop")
            return

    def status_led_color(self) -> LedColor:
        """
        get the color of the RGB status led
        """

        r = int(self.read(IOPin.LED_R).value)
        g = int(self.read(IOPin.LED_G).value)
        b = int(self.read(IOPin.LED_B).value)

        return LedColor((r, g, b))

    def is_load_active(self) -> bool:
        """ 
        return ture if the relay is on
        """

        return self.read(IOPin.RELAY) == IOValue.HIGH


    def hard_reset(self):
        self.write(IOPin.BUTTON_PLUS, BUTTON_DOWN_VALUE)
        self.write(IOPin.BUTTON_MINUS, BUTTON_DOWN_VALUE)

        sleep(7)

        self.write(IOPin.BUTTON_PLUS, BUTTON_UP_VALUE)
        self.write(IOPin.BUTTON_MINUS, BUTTON_UP_VALUE)

        sleep(0.5)

        self.write(IOPin.BUTTON_PLUS, BUTTON_DOWN_VALUE)

        sleep(0.5)

        self.write(IOPin.BUTTON_PLUS, BUTTON_UP_VALUE)

        sleep(2)

    def press_plus(self, press_time=0.2):
        self.write(IOPin.BUTTON_PLUS, BUTTON_DOWN_VALUE)

        sleep(press_time)

        self.write(IOPin.BUTTON_PLUS, BUTTON_UP_VALUE)

    def press_minus(self, press_time=0.2):
        self.write(IOPin.BUTTON_MINUS, BUTTON_DOWN_VALUE)

        sleep(press_time)

        self.write(IOPin.BUTTON_MINUS, BUTTON_UP_VALUE)
