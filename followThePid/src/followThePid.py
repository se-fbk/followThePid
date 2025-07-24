import psutil, subprocess, shlex, logging
from device.factory import Device
from cpu import CPUManager
from metrics import MetricSample, MetricsHandler

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
        
        logging.info(
            f"CPU: {cpu_PIDs:.2f}% | CPU Sys: {cpy_system:.2f}% | "
            f"Rapl: {energy:.2f} uJ | " 
            f"PIDs: {[p.pid for p in self.cpu.get_process_tree()]}"
        ) 

        sample = MetricSample(
            pid = self.cpu.get_pid(),
            cpu_PIDs = cpu_PIDs,
            cpu_system = cpy_system,
            energy = energy
        )

        return sample

    def monitor(self):
        """
        Starts monitoring the process specified by the command.
        """
        if not self.cmd:
            raise ProcessEnergyMonitorError("No command provided to monitor.")
        
        args = shlex.split(self.cmd)
        self.process = subprocess.Popen(args, shell=False)
        self.cpu.set_pid(self.process.pid)

        self.device.setup()  # Start the device monitoring

        # Start monitoring
        try:
            while self.process.poll() is None:
                sample = self._take_measurement()
                
                if sample is not None:
                    self.metrics.add_sample(sample)
                
        except ProcessNotFoundError:
            pass
        
        finally:
            self.device.close()  # Clean up device resources
        
    def summary_csv(self):
        return self.metrics.summary_csv()

    def summary_pandas(self):
        return self.metrics.summary_pandas()

if __name__ == "__main__":

    monitor = FollowThePid(
        cmd="java -javaagent:/Users/pietrolechthaler/git/joularjx-3.0.1.jar -jar /Users/pietrolechthaler/git/EvoMBT-1.2.2-jar-with-dependencies.jar -random -Dsut_efsm=examples.traffic_light -Drandom_seed=123456",
    )
    
    # Start monitoring the process
    monitor.monitor() 

    # Summary
    monitor.summary_csv()