from time import sleep
from logging import getLogger

import pytest

from fw_test.context import Context
from fw_test.io import LedColor


LOGGER = getLogger(__name__)


# adds custom options to the pytest argument parser
def pytest_addoption(parser: pytest.Parser):
    parser.addoption("--config-path", help="path of the environment configuration", default="config.toml")
    parser.addoption("--firmware-path", help="path of the firmware file", required=True)


# load the fixture only one time to reuse connections
@pytest.fixture(scope="session")
def ctx(request: pytest.FixtureRequest):
    context = Context(
        config_path=request.config.getoption("--config-path"),
        firmware_path=request.config.getoption("--firmware-path"),
    )

    yield context

    context.cloud.stop()
    context.io.stop()

# restores the board state before each test
@pytest.fixture(autouse=True)
def before_test_cleanup(ctx: Context):
    LOGGER.info("status LED is %s", ctx.io.status_led_color())

    # ensure firmware is restored before running test
    ctx.io.restore_firmware()

    # flush cloud receive buffer
    ctx.cloud.flush()

    # wait for the system to boot up
    sleep(2)

    if ctx.io.status_led_color() != LedColor.RED:
        LOGGER.info("sending device hard reset")
        ctx.io.hard_reset()

        assert ctx.io.status_led_color() == LedColor.RED

    yield

    ctx.wifi.stop_ap()

