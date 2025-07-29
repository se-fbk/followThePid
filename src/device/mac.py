import subprocess
import threading
import time
import re
from typing import Optional
from collections import deque
from .base import DeviceBase

class DeviceMacOS(DeviceBase):
    POWER_INDICATOR_M_CHIP = "CPU Power:"
    POWER_INDICATOR_INTEL_CHIP = "Intel energy model derived package power (CPUs+GT+SA):"

    def __init__(self, sampling_interval: float):
        """
        sampling_interval: interval in seconds (es. 1.0 → powermetrics -i 1000)
        """
        super().__init__(sampling_interval)
        self.process = None
        self.reader_thread = None
        self.lock = threading.Lock()
        self.samples = deque(maxlen=1000)  # (timestamp, power in W)
        self.latest_power = 0.0
        self.intel_cpu = False
        self.running = False
        #self.setup()

    def setup(self):
        """
        Start the powermetrics command to monitor power consumption.
        This will run in a separate thread to continuously read power data.
        """
        try:
            self.process = subprocess.Popen(
                ["sudo", "powermetrics", "--samplers", "cpu_power", "-i", str(int(self.sampling_interval * 1000))],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                universal_newlines=True,
                bufsize=1
            )
            self.running = True
            self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.reader_thread.start()
        except Exception as e:
            raise RuntimeError(f"Failed to start powermetrics: {e}")

    def _read_loop(self):
        """
        Continuously read from the powermetrics output and parse power data.
        """
        header_checked = False
        if self.process.stdout is None:
            return

        for line in self.process.stdout:
            if not header_checked:
                if line.startswith("EFI version"):
                    self.intel_cpu = True
                if line.strip() == "":
                    header_checked = True
                continue

            power = self._parse_power_line(line)
            if power is not None:
                now = time.time()
                with self.lock:
                    self.latest_power = power
                    self.samples.append((now, power))

            if not self.running:
                break

    def _parse_power_line(self, line: str) -> Optional[float]:
        """
        Parse a line from powermetrics output to extract power in watts.
        Returns None if the line does not contain valid power data.
        """
        try:
            line = line.strip()
            if not line or line.startswith("*"):
                return None

            if self.intel_cpu:
                if self.POWER_INDICATOR_INTEL_CHIP in line:
                    match = re.search(r"([\d.]+)\s*W", line)
                    if match:
                        return float(match.group(1))
            else:
                if self.POWER_INDICATOR_M_CHIP in line and not line.startswith("Combined"):
                    match = re.search(r"([\d]+)\s*mW", line)
                    if match:
                        return float(match.group(1)) / 1000.0
        except Exception:
            pass

        return None

    def get_energy(self) -> float:
        """
        Calculate the energy consumed in microjoules over the sampling interval.
        Returns the energy in microjoules (µJ).
        If no samples are available, returns 0.0.
        """

        now = time.time()
        cutoff = now - self.sampling_interval

        with self.lock:
            powers = [p for t, p in self.samples if t >= cutoff] # filter samples within the last sampling interval

        if not powers:
            return 0.0

        avg_power = sum(powers) / len(powers) # average power in watts
        energy_joules = avg_power * self.sampling_interval # energy in joules
        return energy_joules * 1_000_000  # µJ

    def close(self):
        """
        Stop the powermetrics process and clean up resources.
        """
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join()