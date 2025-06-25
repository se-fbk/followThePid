import psutil
import time
import subprocess
import shlex
from datetime import datetime
from typing import List, Optional
from pyJoules.device.rapl_device import Domain, RaplPackageDomain
from pyJoules.energy_meter import EnergyMeter
from pyJoules.device.device_factory import DeviceFactory
from pyJoules.handler.pandas_handler import PandasHandler
import pandas as pd

from handler import ProcessEnergySample

class ProcessEnergyMonitorError(Exception):
    pass

class ProcessNotFoundError(ProcessEnergyMonitorError):
    pass

class ProcessEnergyMonitor:
    def __init__(self, cmd: str, domains: Optional[List[Domain]], sampling_interval: float = 0.1):
        """
        Initializes the energy monitor for a specific process.

        Args:
            cmd (str, optional): A shell command to execute and monitor.
            sampling_interval (float): Sampling interval in seconds.
        """

        self.cmd = cmd
        
        self.sampling_interval = sampling_interval
        
        self.domains = domains
        self.devices = DeviceFactory.create_devices(domains)
        self.meter = EnergyMeter(devices=self.devices)
        self.cpu_meter = pd.DataFrame(columns=['tag', 'cpu'])
        self.handler = PandasHandler()

        self.num_cores = psutil.cpu_count(logical=True) or 1 # number of logical CPU cores

        self.reset_state()

    def reset_state(self):
        """
        Resets internal state before starting a new monitoring session.
        """
        self.start_time = datetime.now()
        self.total_rapl = 0.0
        self.total_process = 0.0
        self.process_tree = []
        self.cpu_meter = pd.DataFrame(columns=['tag', 'cpu'])
        self.counter = 1

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
        try:
            self.process_tree = self.get_process_tree()
            print(f"Monitoring process tree for PID {self.pid}: {[p.pid for p in self.process_tree]}")
        except ProcessNotFoundError:
            return None

        self.warmup_cpu()

        # Wait for delta accumulation
        time.sleep(self.sampling_interval)

        cpu_total = 0.0
        for p in self.process_tree:
            try:
                cpu_p = p.cpu_percent(interval=None) / self.num_cores  # Normalize by number of cores
                cpu_total += cpu_p
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if cpu_total == 0.0:
            return None

        # Measure total system CPU
        cpu_system = psutil.cpu_percent(interval=0.0)

        # Record RAPL energy for this sample
        self.meter.record(tag=f"{self.counter}")

        print(
            f"PID {self.pid} | "
            f"CPU: {cpu_total:.2f}% [Total system: {cpu_system:.2f}%] | "
        )

        sample = [{'tag': self.counter, 'cpu': cpu_total}]
        self.counter += 1
        return sample


    def monitor(self):
        """
        Continuously monitors the process until it terminates.
        """

        args = shlex.split(self.cmd)
        self.process = subprocess.Popen(args, shell=False)
        self.pid = self.process.pid
       
        # Start monitoring RAPL
        self.meter.start(tag="0")

        try:
            while self.process.poll() is None:
                cpu_sample = self.take_measurement()

                if cpu_sample is not None:
                    self.cpu_meter = pd.concat([self.cpu_meter, pd.DataFrame(cpu_sample)], ignore_index=True)
                
                # Wait for the next cpu measurement
                time.sleep(self.sampling_interval) 

        except ProcessNotFoundError:
            pass
        
        # Stop monitoring RAPL
        self.meter.stop()

        self.handler.process(self.meter.get_trace())
        rapl_df = self.handler.get_dataframe()

        # Rename the last column to 'rapl'
        last_col_name = rapl_df.columns[-1]
        rapl_df = rapl_df.rename(columns={last_col_name: 'rapl'})
        
        # Total RAPL energy after process termination
        self.total_rapl = rapl_df.iloc[:, -1].sum() / 1_000_000 # Convert to Joules
        
        # Total energy for the process
        self.total_process = self.calculate_process_energy(rapl_df, self.cpu_meter)
        
        print(f"Domain energy consumption: {self.total_rapl:.2f} J")
        print(f"Total process energy consumption: {self.total_process:.2f} J")
        
    
    def calculate_process_energy(self, rapl_df, cpu_df) -> float:
        """
        Calculates the total energy consumed by the process based on CPU usage.

        Returns:
            float: Total energy consumed by the process in Joules.
        """

        rapl_df['tag'] = rapl_df['tag'].astype(int)
        cpu_df['tag'] = cpu_df['tag'].astype(int)
        df_merged = pd.merge(rapl_df, cpu_df, on='tag')
        df_merged['energy_uJ'] = (df_merged['cpu'] / 100) * df_merged['rapl']        
        
        return df_merged["energy_uJ"].sum() / 1_000_000 # Convert to Joules

if __name__ == "__main__":
    monitor = ProcessEnergyMonitor(domains=[RaplPackageDomain(0)],cmd="java -jar /home/pietrofbk/git/iv4xr-mbt/target/EvoMBT-1.2.2-jar-with-dependencies.jar -random -Dsut_efsm=examples.traffic_light -Drandom_seed=123456")
    monitor.monitor()
