from fw_test.wifi import Wifi
from fw_test.cloud import Cloud
from fw_test.io import IO
from fw_test.config import Config
from fw_test.firmware import Firmware
from fw_test.api import LocalApi


class Context:
    """
    main context exposed to the test runner
    """

    def __init__(self, config_path: str, firmware_path: str):
        self.config = Config.load_file(config_path)
        self.firmware = Firmware.load_file(firmware_path)
        self.prev_firmware = Firmware.load_file(self.config.prev_firmware_path)
        self.io = IO(self.config)
        self.wifi = Wifi(self.config)
        self.cloud = Cloud(self.config)
        self.api = LocalApi(self.config)

