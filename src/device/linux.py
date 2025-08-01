import os
from .base import DeviceBase
import logging

class DeviceLinux(DeviceBase):
    
    BASE_PATH = "/sys/class/powercap/intel-rapl/"

    def __init__(self, sampling_interval, sockets: int = 1):
        super().__init__(sampling_interval)
        self.sockets = sockets
        
        self.setup()

        self.last_energy = [self._read_domain(domain) for domain in self.domains]
        self.max_energy = [self._get_max_energy(domain) for domain in self.domains]

    def _is_readable(self, path: str) -> bool:
        """
        Check if the given path is a directory and contains the 'energy_uj' file.
        """
        return os.path.isdir(path) and os.access(os.path.join(path, "energy_uj"), os.R_OK)

    def _get_rapl_candidates(self):
        """
        Get all RAPL domains that start with 'intel-rapl:'.
        """
        if not os.path.exists(self.BASE_PATH):
            raise RuntimeError(f"RAPL base path not found: {self.BASE_PATH}")

        # Return a list of RAPL domains that start with 'intel-rapl:'
        return [
            os.path.join(self.BASE_PATH, entry)
            for entry in os.listdir(self.BASE_PATH)
            if entry.startswith("intel-rapl:")
        ]

    def setup(self) -> str:
        """
        Set up the RAPL domains for the specified number of sockets.
        """
       
        candidates = self._get_rapl_candidates()

        # Filter candidates to only include package domains and with readability permissions
        package_domains = [
            path for path in candidates
            if self._is_readable(path) and self._get_device_name(path).startswith("package")
        ]

        if len(package_domains) < self.sockets:
            raise RuntimeError(f"Could not find {self.sockets} package RAPL sources, found only {len(package_domains)}")

        self.domains = package_domains[:self.sockets]
        logging.info(f"Using RAPL domains: {self.domains}")

    def _read_domain(self, domain):
        """
        Read the energy consumption from the RAPL domain.
        """
        try:
            with open(os.path.join(domain, "energy_uj")) as f:
                return float(f.read().strip())  # uJ
        except Exception as e:
            raise RuntimeError(f"Error reading energy_uj for {domain}: {e}")
       
    def _get_max_energy(self, domain):
        """
        Read the maximum energy range from the RAPL domain.
        """
        try:
            with open(os.path.join(domain, "max_energy_range_uj")) as f:
                return float(f.read().strip())
        except Exception as e:
            raise RuntimeError(f"Error reading max_energy_range_uj for {domain}: {e}")
        
    def _get_device_name(self, domain):
        """
        Read the device name from the RAPL domain.
        """
        try:
            with open(os.path.join(domain, "name")) as f:
                return str(f.read().strip())
        except Exception as e:
            raise RuntimeError(f"Error reading device name for {domain}: {e}")

    def get_energy(self):
        """
        Get total energy usage across all configured sockets.
        """
        total_energy = 0.0
        
        for i, domain in enumerate(self.domains):
            try:
                current_energy = self._read_domain(domain)

                # Overflow handling
                if current_energy < self.last_energy[i]:
                    energy_used = (self.max_energy[i] - self.last_energy[i]) + current_energy
                else:
                    energy_used = current_energy - self.last_energy[i]

                self.last_energy[i] = current_energy
                total_energy += energy_used
            except Exception as e:
                raise RuntimeError(f"Error calculating energy consumption for {domain}: {e}")

        return total_energy

            
    def close(self):
        pass