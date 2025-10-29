from ..device.factory import DeviceBase
import logging

class DeviceWindows(DeviceBase):
    def get_energy(self):
        logging.warning("Energy measurement until now is not supported on Windows.")
