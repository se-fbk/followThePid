import os
from .device_base import DeviceBase

class DeviceLinux(DeviceBase):
    SOURCES = [
        "/sys/class/powercap/intel-rapl:1/",
        "/sys/class/powercap/intel-rapl:0/",
        "/sys/class/powercap/intel-rapl:0:0/"
    ]

    def __init__(self):
        super().__init__()
        self.domain = self.setup()

    def _is_readable(self, path: str) -> bool:
        """
        Check if the given path is a directory and contains the 'energy_uj' file.
        """
        return os.path.isdir(path) and os.access(os.path.join(path, "energy_uj"), os.R_OK)

    def setup(self) -> str:
        """
        Find a readable RAPL source
        """
        for path in self.SOURCES:
            if self._is_readable(path):
                return path
        raise RuntimeError("No readable RAPL source found.")

    def get_energy(self):
        """
        Read the energy consumption from the RAPL domain.
        """
        try:
            with open(os.path.join(self.domain, "energy_uj")) as f:
                return float(f.read().strip())
        except Exception as e:
            raise RuntimeError(f"Error reading energy_uj: {e}")

    def get_max_energy(self):
        """
        Read the maximum energy range from the RAPL domain.
        """
        try:
            with open(os.path.join(self.domain, "max_energy_range_uj")) as f:
                return float(f.read().strip())
        except Exception as e:
            raise RuntimeError(f"Error reading max_energy_range_uj: {e}")
        
    def get_device_name(self):
        """
        Read the device name from the RAPL domain.
        """
        try:
            with open(os.path.join(self.domain, "name")) as f:
                return str(f.read().strip())
        except Exception as e:
            raise RuntimeError(f"Error reading device name: {e}")
