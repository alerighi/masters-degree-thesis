from fw_test.wifi import Wifi
from fw_test.cloud import Cloud
from fw_test.io import IO
from fw_test.config import Config


class Context:
    """
    main context exposed to the test runner
    """

    def __init__(self, config_path: str):
        self.config = Config.load(config_path)
        self.io = IO(self.config)
        self.wifi = Wifi(self.config)
        self.cloud = Cloud(self.config)

