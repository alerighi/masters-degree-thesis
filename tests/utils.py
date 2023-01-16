from enum import Enum

from fw_test.context import Context
from fw_test.io import IOPin, IOValue


class LedColor(Enum):
    OFF = (0, 0, 0)
    RED = (1, 0, 0)
    GREEN = (0, 1, 0)
    BLUE = (0, 0, 1)
    YELLOW = (1, 1, 0)
    CYAN = (0, 1, 1)
    MAGENTA = (1, 0, 1)
    WHITE = (1, 1, 1)


def assert_status_led_color(ctx: Context, color: LedColor):
    """
    checks that the status LED is of the specified color
    """

    r, g, b = color.value()

    assert ctx.io.read(IOPin.LED_R) == IOValue.HIGH if r else IOValue.LOW
    assert ctx.io.read(IOPin.LED_G) == IOValue.HIGH if g else IOValue.LOW
    assert ctx.io.read(IOPin.LED_B) == IOValue.HIGH if b else IOValue.LOW

