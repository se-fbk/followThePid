import os
import time
from .base import DeviceBase

class DeviceLinux(DeviceBase):
    SOURCES = [
        "/sys/class/powercap/intel-rapl:1/",
        "/sys/class/powercap/intel-rapl:0/",
        "/sys/class/powercap/intel-rapl:0:0/"
    ]

    def __init__(self, sampling_interval):
        super().__init__(sampling_interval)
        self.domain = self.setup()

        self.last_energy = self._read_domain()
        self.max_energy = self._get_max_energy()

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
                print(f"Using RAPL source: {path}")
                return path
        raise RuntimeError("No readable RAPL source found.")

    def _read_domain(self):
        """
        Read the energy consumption from the RAPL domain.
        """
        try:
            with open(os.path.join(self.domain, "energy_uj")) as f:
                return float(f.read().strip()) # uJ
        except Exception as e:
            raise RuntimeError(f"Error reading energy_uj: {e}")
       
    def _get_max_energy(self):
        """
        Read the maximum energy range from the RAPL domain.
        """
        try:
            with open(os.path.join(self.domain, "max_energy_range_uj")) as f:
                return float(f.read().strip())
        except Exception as e:
            raise RuntimeError(f"Error reading max_energy_range_uj: {e}")
        
    def _get_device_name(self):
        """
        Read the device name from the RAPL domain.
        """
        try:
            with open(os.path.join(self.domain, "name")) as f:
                return str(f.read().strip())
        except Exception as e:
            raise RuntimeError(f"Error reading device name: {e}")

    def get_energy(self):
        try:
            current_energy = self._read_domain()

            # Overflow handling
            if current_energy < self.last_energy:
                energy_used = (self.max_energy - self.last_energy) + current_energy

            else:
                energy_used = current_energy - self.last_energy

            self.last_energy = current_energy
            return energy_used
        
        except Exception as e:
            raise RuntimeError(f"Error calculating energy consumption: {e}")
            
    def close(self):
        pass