import psutil

class CPUManager():
    """
    Manages CPU usage monitoring for a specific process
    """
    
    def __init__(self, sampling_interval: float, num_cores: int):
        """
        :param sampling_interval: Time in seconds between each CPU usage measurement.
        :param num_cores: Number of CPU cores to normalize the CPU usage.
        """

        self.sampling_interval = sampling_interval
        self.num_cores = num_cores
        self.pid = None
        self.process_tree = []


    def set_pid(self, pid: int):
        """
        Sets the PID for which CPU usage will be monitored.
        :param pid: Process ID to monitor.
        """
        self.pid = pid

    def get_pid(self) -> int:
        """
        Returns the PID being monitored.
        :return: Process ID.
        """
        return self.pid

    def _warmup_cpu(self):
        """
        Performs a warm-up CPU usage measurement for all processes in the tree
        """
        self.process_tree = self._get_process_tree()
        
        try:
            for p in self.process_tree:
                p.cpu_percent(interval=None) # initialize CPU
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  
    
    def _get_process_tree(self) -> list:
        """
        Retrieves the main process and all of its child processes.
        """
        try:
            main_process = psutil.Process(self.pid)
            return [main_process] + main_process.children(recursive=True)
        except psutil.NoSuchProcess:
            raise Exception(f"Process {self.pid} not found")
        
    def get_cpu_usage(self) -> float:
        """
        Measures the CPU usage of the monitored process.
        :return: CPU usage as a percentage normalized by the number of cores.
        """
        if not self.process_tree:
            self._warmup_cpu()

        cpu_total = 0.0
        for p in list(self.process_tree):
            try:
                cpu_p = p.cpu_percent(interval=None) / self.num_cores
                cpu_total += cpu_p
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return cpu_total / 100.0

    def get_cpu_system(self) -> float:
        """
        Measures the system-wide CPU usage.
        :return: System CPU usage as a percentage.
        """
        
        cpu_system = psutil.cpu_percent(interval=0.0)
        
        # avoid division by zero
        if cpu_system == 0.0:
            return None 
        
        return cpu_system / 100.0
    
    def get_process_tree(self) -> list:
        return self.process_tree