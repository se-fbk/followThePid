import psutil
import time
from datetime import datetime
from typing import List, Optional
from pyJoules.energy_meter import EnergyMeter
from pyJoules.device.rapl_device import RaplPackageDomain
from pyJoules.device.device_factory import DeviceFactory

from handler import ProcessEnergySample, ProcessEnergyHandler
from csv_handler import CSVHandler

class ProcessEnergyMonitorError(Exception):
    pass

class ProcessNotFoundError(ProcessEnergyMonitorError):
    pass

class ProcessEnergyMonitor:
    def __init__(self, pid: int, handler: ProcessEnergyHandler, socket: int = 0, sampling_interval: float = 0.1):
        self.pid = pid
        self.handler = handler
        self.sampling_interval = sampling_interval
        self.socket = socket
        self.num_cores = psutil.cpu_count(logical=True) or 1

        # TODO: check if the socket is valid, auto detect if not provided
        domains = [RaplPackageDomain(socket)]
        devices = DeviceFactory.create_devices(domains)
        self.meter = EnergyMeter(devices)

        self.reset_state()

    def reset_state(self):
        """
        Resets the internal state of the monitor
        """
        self.start_time = datetime.now()
        self.total_rapl = 0.0
        self.total_process = 0.0
        self._process_tree = []

    def _get_process_tree(self) -> List[psutil.Process]:
        """
        Retrieves the process tree for the given PID.
        """

        try:
            main_process = psutil.Process(self.pid)
            return [main_process] + main_process.children(recursive=True)
        except psutil.NoSuchProcess:
            raise ProcessNotFoundError(f"Process {self.pid} not found")

    def calculate_proc_energy(self, proc: psutil.Process, total_energy: float) -> float:
        """
        Calculates the energy consumed by a specific process based on its CPU usage.
        """
        try:
            cpu_percent = proc.cpu_percent(interval=0.1)
            return cpu_percent, total_energy * ((cpu_percent / 100) / self.num_cores)
        except Exception:
            return 0.0
        
    def warmup_cpu(self):
        
        try:
            self._process_tree = self._get_process_tree()
            for p in self._process_tree:
                p.cpu_percent(interval=0.1)
        except Exception:
            pass

    def take_measurement(self) -> Optional[ProcessEnergySample]:
        """
        Takes a measurement of the energy consumed by the process and its children.
        """
        try:
            self._process_tree = self._get_process_tree()
            print(f"Monitoring process tree for PID {self.pid}: {[p.pid for p in self._process_tree]}")
        except ProcessNotFoundError:
            return None

        self.meter.start()
        time.sleep(self.sampling_interval)
        self.meter.stop()

        energy_data = self.meter.get_trace()
        if not energy_data:
            return None

        # Get last RAPL energy measurement
        last = energy_data[-1]
        energy_by_domain = last.energy
        current_rapl = sum(energy_by_domain.values())  # µJ
        self.total_rapl += current_rapl

        # Calculate total process energy
        cpu_total = 0.0
        current_process = 0.0

        for p in self._process_tree:
            try:
                cpu_p, energy_p = self.calculate_proc_energy(p, current_rapl)
                current_process += energy_p
                cpu_total += cpu_p
            except psutil.NoSuchProcess:
                continue

        self.total_process += current_process
        
        # Debug print
        print(  
            f"PID {self.pid} | "
            f"CPU: {cpu_total} | "
            f"Proc: {current_process / 1_000_000:.2f} J | "
            f"Tot Proc: {self.total_process / 1_000_000:.2f} J | "
            f"Tot RAPL: {self.total_rapl / 1_000_000:.2f} J"
        )

        return ProcessEnergySample(
            timestamp=datetime.now(),
            pid=self.pid,
            cpu_percent=cpu_total,
            process_energy=current_process,
            rapl_energy=self.total_rapl
        )

    def monitor(self):
        self.reset_state()
        self.warmup_cpu()

        try:
            while psutil.pid_exists(self.pid) and psutil.Process(self.pid).is_running():
                sample = self.take_measurement()
                # if sample:
                #     self.handler.handle(sample)
        except ProcessNotFoundError:
            pass

        self.log_summary()

    def log_summary(self):
        duration = datetime.now() - self.start_time
        summary = {
            'duration': str(duration),
            'total_process': self.total_process,
            'total_rapl': self.total_rapl,
        }
        self.handler.handle_summary(summary)

if __name__ == "__main__":
    pid = int(input("Enter PID to monitor: "))
    handler = CSVHandler()
    monitor = ProcessEnergyMonitor(pid=pid, handler=handler)
    monitor.monitor()
