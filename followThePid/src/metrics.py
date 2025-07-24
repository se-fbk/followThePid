
import pandas as pd
import csv

class MetricSample():
    """
    Represents a single measurement sample for process energy monitoring.
    """

    def __init__(self, pid: int, cpu_PIDs: float, cpu_system:float, energy: float):
        self.pid = pid
        self.cpu_PIDs = cpu_PIDs
        self.cpu_system = cpu_system
        self.energy = energy

class MetricsHandler():
    """
    Handles the collection and processing of energy samples for a monitored process.
    """

    def __init__(self):
        """
        Initializes the MetricsHandler with a sampling interval and number of CPU cores.
        
        :param sampling_interval: Time in seconds between each measurement.
        :param num_cores: Number of CPU cores to normalize CPU usage.
        """
        self.samples = []


    def add_sample(self, sample: MetricSample):
        """
        Adds a new energy sample to the handler.
        """
        self.samples.append(sample)

    def _get_system_energy(self) -> float:
        """
        Calculates the total energy consumed by the system (Joule) based on the first and last samples.
        """
        first_energy = self.samples[0].energy if self.samples else 0.0
        last_energy = self.samples[-1].energy if self.samples else 0.0

        return (last_energy - first_energy) / 1_000_000  # Convert from microjoules to joules

    def _get_pid_energy(self) -> float:
        """
        Calculates the total energy consumed by the process (Joule) based on the samples.
        """
        # At least two samples are needed to calculate energy consumption
        if len(self.samples) < 2: 
            return 0.0

        total_energy = 0.0

        for prev, curr in zip(self.samples, self.samples[1:]):
            energy_delta = curr.energy - prev.energy  # uJ
            cpu_usage = curr.cpu_PIDs  # [0,1]
            cpu_system = curr.cpu_system # [0,1]

            total_energy += (energy_delta * cpu_usage) / cpu_system

        return total_energy / 1_000_000  # Convert from microjoules to joules


    def _get_last_sample(self):
        """
        Returns the last sample taken.
        """
        if self.samples:
            return self.samples[-1]
        return None

    def summary_pandas(self):
        """
        Converts the energy samples into a Pandas DataFrame
        """
        if not self.samples:
            return pd.DataFrame()
        
        data = [{
            "pid": sample.pid,
            "cpu_PIDs": sample.cpu_PIDs,
            "cpu_system": sample.cpu_system,
            "energy_uj": sample.energy
        } for sample in self.samples]

        df = pd.DataFrame(data)
        return df
    
    def summary_csv(self, filename: str = "followThePid_report.csv"):
        """
        Writes the energy consumption summary to a CSV file.
        """
        if not self.samples:
            return False
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["pid", "cpu_PIDs", "cpu_system", "energy_uj"])
            for sample in self.samples:
                writer.writerow([sample.pid, sample.cpu_PIDs, sample.cpu_system, sample.energy])

        return True