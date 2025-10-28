import psutil, subprocess, shlex, logging, os, time
from .device.factory import Device
from .cpu import CPUManager
from .metrics import MetricSample, MetricsHandler


class ProcessEnergyMonitorError(Exception):
    def __init__(self, message="An error occurred in the energy monitor."):
        super().__init__(message)

class ProcessNotFoundError(ProcessEnergyMonitorError):
    def __init__(self, pid=None, message=None):
        msg = message or f"Process with PID {pid} not found." if pid else "Process not found."
        super().__init__(msg)

class FollowThePid:
    def __init__(self, cmd: str, sampling_interval: float = 0.1):
        """
        Initializes the energy monitor for a specific process.

        Args:
            cmd (str, optional): A shell command to execute and monitor
            sampling_interval (float): Sampling interval in seconds
        """

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.cmd = cmd
        self.sampling_interval = sampling_interval
        
        self.device = Device(sampling_interval=sampling_interval)
        self.cpu = CPUManager(sampling_interval=sampling_interval, num_cores=psutil.cpu_count(logical=True) or 1)
        self.metrics = MetricsHandler()
        
    def _take_measurement(self):
        cpu_PIDs = self.cpu.get_cpu_usage() # % [0,1]
        cpy_system = self.cpu.get_cpu_system() # % [0,1]

        if cpu_PIDs is None or cpy_system is None:
            return None
        
        energy = self.device.get_energy()  # uJ
        
        # logging.info(
        #     f"CPU: {cpu_PIDs:.2f} | CPU Sys: {cpy_system:.2f} | "
        #     f"Rapl: {energy:8f} uJ | " 
        #     f"PIDs: {[p.pid for p in self.cpu.get_process_tree()]}"
        # ) 

        sample = MetricSample(
            pid = self.cpu.get_pid(),
            cpu_PIDs = cpu_PIDs,
            cpu_system = cpy_system,
            energy = energy
        )

        return sample

    def monitor(self, timeout: int = 10000):
        """
        Starts monitoring the process specified by the command.
        """
        logging.info("Starting process monitoring")

        if not self.cmd:
            raise ProcessEnergyMonitorError("No command provided to monitor.")
        
        args = shlex.split(self.cmd)

        if timeout is not None and timeout <= 0:
            raise ValueError("Timeout must be a positive integer or None.")
                    
        self.process = subprocess.Popen(args, shell=False)
        self.cpu.set_pid(self.process.pid)

        start_time = time.time()

        # Start monitoring
        try:
            while self.process.poll() is None:
                if timeout and (time.time() - start_time) > timeout:
                    logging.warning("Timeout reached. Killing the process.")
                    self.process.kill()
                    break
                
                sample = self._take_measurement()
                
                if sample is not None:
                    self.metrics.add_sample(sample)
                
        except ProcessNotFoundError:
            pass
        
        finally:
            self.device.close()  # Clean up device resources

        logging.info("Process monitoring terminated")
        
        
    def samples_csv(self, filename: str = "followThePid_samples.csv"):
        logging.info("Generating CSV of samples at %s", filename)

        if not self.metrics.samples_csv(filename):
            logging.error("Failed to generate CSV report")
            return False

        return True

    def samples_pandas(self):
        logging.info("Generating Pandas DataFrame for samples")
        return self.metrics.samples_pandas()
    
    def get_pid_energy(self) -> float:
        """
        Returns the total energy consumed by the process in Joules.
        """
        energy = self.metrics.get_pid_energy()
        logging.info(f"Total energy consumed by PID {self.cpu.get_pid()}: {energy:.2f} J")
        return energy

if __name__ == "__main__":

    # Example usage
    base_dir = os.path.dirname(os.path.abspath(__file__))

    monitor = FollowThePid(
        cmd=f"python3 {base_dir}/example/simple_example.py"
    )
    
    # Start monitoring the process
    monitor.monitor() 

    # Save the samples to a CSV file
    monitor.samples_csv()

    total_energy = monitor.get_pid_energy()