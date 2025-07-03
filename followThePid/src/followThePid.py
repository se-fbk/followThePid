import psutil, time, subprocess, shlex, logging
from device.device import Device
from typing import Optional
from handler import ProcessEnergySample, ProcessEnergyHandler, CSVHandler, PandasHandler

class ProcessEnergyMonitorError(Exception):
    pass

class ProcessNotFoundError(ProcessEnergyMonitorError):
    pass

class FollowThePid:
    def __init__(self, cmd: str, sampling_interval: float = 0.1, handler: Optional[ProcessEnergyHandler] = None):
        """
        Initializes the energy monitor for a specific process.

        Args:
            cmd (str, optional): A shell command to execute and monitor
            domains (List[Domain], optional): List of RAPL domains to monitor
            sampling_interval (float): Sampling interval in seconds
            handler (ProcessEnergyHandler, optional): Handler for processing energy samples
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.cmd = cmd
        self.sampling_interval = sampling_interval
        self.device = Device()

        if not self.device:
            raise ProcessEnergyMonitorError("No RAPL device found. Ensure you are running on a supported platform with RAPL support.")
        
        logging.info(f"Using RAPL device: {self.device.domain}")

        self.handler = handler if handler is not None else CSVHandler()
        self.num_cores = psutil.cpu_count(logical=True) or 1 
        
        self.reset_state()


    def reset_state(self):
        """
        Resets internal state before starting a new monitoring session.
        """
        self.process_tree = []
        self.counter = 0

    def get_process_tree(self) -> list:
        """
        Retrieves the main process and all of its child processes.
        """
        try:
            main_process = psutil.Process(self.pid)
            return [main_process] + main_process.children(recursive=True)
        except psutil.NoSuchProcess:
            raise ProcessNotFoundError(f"Process {self.pid} not found")
        
    def warmup_cpu(self):
        """
        Performs a warm-up CPU usage measurement for all processes in the tree
        """
        try:
            for p in self.process_tree:
                p.cpu_percent(interval=None) # initialize CPU
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  
    
    def take_measurement(self) -> Optional[ProcessEnergySample]:

        try:
            self.process_tree = self.get_process_tree()
        except ProcessNotFoundError:
            return None

        self.warmup_cpu()
        time.sleep(self.sampling_interval) # Wait for sampling interval
        cpu_total = 0.0
        for p in self.process_tree: 
            try:
                cpu_p = p.cpu_percent(interval=None) / self.num_cores  # normalize by number of cores
                cpu_total += cpu_p

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        energy = self.device.get_energy() #uJ
        cpu_system = psutil.cpu_percent(interval=0.0)
        
        # avoid division by zero
        if cpu_system == 0.0:
            return None 

        logging.info(
            f"CPU: {cpu_total:.2f}% | CPU Sys: {cpu_system:.2f}%] | "
            f"Rapl: {energy:.2f} uJ | " 
            f"PIDs: {[p.pid for p in self.process_tree]}"
        ) # debug print

        sample = ProcessEnergySample(
            id = self.counter,
            pid = self.pid,
            cpu_percent = cpu_total / 100, # [0,1]
            cpu_system = cpu_system / 100, # [0,1]
            energy = energy, # uJ
        )

        self.counter += 1
        return sample

    def monitor(self):
        """
        Continuously monitors the process until it terminates
        """
        args = shlex.split(self.cmd)
        self.process = subprocess.Popen(args, shell=False)
        self.pid = self.process.pid

        # Start monitoring
        try:
            while self.process.poll() is None:
                sample = self.take_measurement()
                if sample is not None:
                    self.handler.add_sample(sample)
                
        except ProcessNotFoundError:
            pass
        
        total_rapl_system = self.handler.get_system_energy()
        total_rapl_pid = self.handler.get_pid_energy()
        
        logging.info(f"Domain energy consumption: {total_rapl_system:.2f} J")
        logging.info(f"Total process energy consumption: {total_rapl_pid:.2f} J")
        
if __name__ == "__main__":

    # Test ProcessEnergyMonitor with a Pandas Handler
    handler = PandasHandler()
    monitor = FollowThePid(
        cmd="java -jar /home/pietrofbk/git/iv4xr-mbt/target/EvoMBT-1.2.2-jar-with-dependencies.jar -random -Dsut_efsm=examples.traffic_light -Drandom_seed=123456",
        handler=handler
    )
    
    monitor.monitor()
    df = handler.summary()
    print(df)