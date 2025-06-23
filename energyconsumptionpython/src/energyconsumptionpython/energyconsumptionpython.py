import psutil
import time
import subprocess
from datetime import datetime
from typing import List, Optional
from pyJoules.energy_meter import EnergyMeter
from pyJoules.device.rapl_device import RaplPackageDomain
from pyJoules.device.device_factory import DeviceFactory

from handler import ProcessEnergySample, ProcessEnergyHandler
from csv_handler import CSVHandler
from utils import detect_sockets

class ProcessEnergyMonitorError(Exception):
    pass

class ProcessNotFoundError(ProcessEnergyMonitorError):
    pass

class ProcessEnergyMonitor:
    def __init__(self, cmd: str, handler: ProcessEnergyHandler, sampling_interval: float = 0.1):
        """
        Initializes the energy monitor for a specific process.

        Args:
            cmd (str, optional): A shell command to execute and monitor.
            handler (ProcessEnergyHandler): Handler for processing energy samples and summaries.
            sampling_interval (float): Sampling interval in seconds.
        """

        self.cmd = cmd
        self.handler = handler
        self.sampling_interval = sampling_interval

        self.sockets = detect_sockets()
        domains = [RaplPackageDomain(socket_id) for socket_id in self.sockets]

        devices = DeviceFactory.create_devices(domains)
        self.meter = EnergyMeter(devices)

        # Get number of logical CPU cores
        self.num_cores = psutil.cpu_count(logical=True) or 1

        self.reset_state()

    def reset_state(self):
        """
        Resets internal state before starting a new monitoring session.
        """
       
        self.start_time = datetime.now()
        self.total_rapl = 0.0
        self.total_process = 0.0
        self.process_tree = []

    def get_process_tree(self) -> List[psutil.Process]:
        """
        Retrieves the main process and all of its child processes.

        Returns:
            List[psutil.Process]: The complete process tree.

        Raises:
            ProcessNotFoundError: If the main process does not exist.
        """

        try:
            main_process = psutil.Process(self.pid)
            return [main_process] + main_process.children(recursive=True)
        except psutil.NoSuchProcess:
            raise ProcessNotFoundError(f"Process {self.pid} not found")
        
    def warmup_cpu(self):
        """
        Performs a warm-up CPU usage measurement for all processes in the tree.
        This initializes internal CPU counters for accurate measurement.
        """
        try:
            for p in self.process_tree:
                p.cpu_percent(interval=None) # initialize CPU
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  

    def take_measurement(self) -> Optional[ProcessEnergySample]:
        """
        Takes a single energy measurement for the process and its children.

        Returns:
            ProcessEnergySample or None if measurement failed or the process ended.
        """

        try:
            self.process_tree = self.get_process_tree()
            print(f"Monitoring process tree for PID {self.pid}: {[p.pid for p in self.process_tree]}")
        except ProcessNotFoundError:
            return None

        self.warmup_cpu()

        # Measure total system CPU usage
        cpu_system = psutil.cpu_percent(interval=None)

        # Start energy measurement
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

        # Estimate energy usage of each process in the tree
        cpu_total = 0.0
        current_process = 0.0

        for p in self.process_tree:
            try:
                
                cpu_p = p.cpu_percent(interval=None)
                cpu_normalized = cpu_p / self.num_cores

                energy_p = current_rapl * ( cpu_normalized / 100 )

                current_process += energy_p
                cpu_total += cpu_normalized
                
            except psutil.NoSuchProcess:
                continue

        self.total_process += current_process

        # Debug output
        print(  
            f"PID {self.pid} | "
            f"CPU: {cpu_total:.2f} [{cpu_system:.2f}%] | "
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
        """
        Continuously monitors the process until it terminates.
        """

        self.reset_state()

        if self.cmd:
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.pid = self.process.pid
        else:
            raise ValueError("No command provided to monitor.")

        try:
            while psutil.pid_exists(self.pid) and psutil.Process(self.pid).is_running():
                sample = self.take_measurement()
                # if sample:
                #     self.handler.handle(sample)
        except ProcessNotFoundError:
            pass

        self.log_summary()

    def log_summary(self):
        """
        Logs and passes the total energy summary to the handler.
        """
        duration = datetime.now() - self.start_time
        summary = {
            'duration': str(duration),
            'total_process': self.total_process,
            'total_rapl': self.total_rapl,
        }
        self.handler.handle_summary(summary)

if __name__ == "__main__":
    handler = CSVHandler()
    monitor = ProcessEnergyMonitor(cmd="python3 cpu.py", handler=handler)
    monitor.monitor()
