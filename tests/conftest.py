from time import sleep

import pytest

from fw_test.context import Context


# adds custom options to the pytest argument parser
def pytest_addoption(parser: pytest.Parser):
    parser.addoption("--config-path", help="path of the environment configuration", default="config.toml")
    parser.addoption("--firmware-path", help="path of the firmware file", required=True)


# load the fixture only one time to reuse connections
@pytest.fixture(scope="session")
def ctx(request: pytest.FixtureRequest):
    return Context(
        config_path=request.config.getoption("--config-path"),
        firmware_path=request.config.getoption("--firmware-path"),
    )


# restores the board state before each test
@pytest.fixture(autouse=True)
def before_test_cleanup(ctx: Context):
    # ensure firmware is restored before running test
    ctx.io.restore_firmware()

    # flush cloud receive buffer
    ctx.cloud.flush()

    # wait for the system to boot up
    sleep(2)

    yield

    # do any cleanup operation may be needed

