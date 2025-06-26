from typing import Dict
import pandas as pd
import csv

class ProcessEnergySample:
    def __init__(self, id: int, pid: int, cpu_percent: float, energy: float):
        self.id = id
        self.pid = pid
        self.cpu_percent = cpu_percent
        self.energy = energy

class ProcessEnergyHandler:

    def __init__(self):
        """
        Initializes the handler for process energy samples.
        """
        self.samples = []

    def add_sample(self, sample: ProcessEnergySample):
        """
        Adds a new energy sample to the handler.
        """
        self.samples.append(sample)
    
    def get_system_energy(self) -> float:
        """
        Calculates the total energy consumed by the system (Joule) based on the first and last samples.
        """
        first_energy = self.samples[0].energy if self.samples else 0.0
        last_energy = self.samples[-1].energy if self.samples else 0.0

        return (last_energy - first_energy) / 1_000_000  # Convert from microjoules to joules

    def get_pid_energy(self) -> float:
        """
        Calculates the total energy consumed by the process (Joule) based on the samples.
        """
        # At least two samples are needed to calculate energy consumption
        if len(self.samples) < 2: 
            return 0.0

        total_energy = 0.0

        for prev, curr in zip(self.samples, self.samples[1:]):
            energy_delta = curr.energy - prev.energy  # delta energia totale (µJ)
            cpu_usage = curr.cpu_percent  # valore normalizzato [0,1]
            total_energy += energy_delta * cpu_usage

        return total_energy / 1_000_000  # Convert from microjoules to joules

    
    def get_last_sample(self) -> ProcessEnergySample:
        if self.samples:
            return self.samples[-1]
        return None

    def summary(self, summary: Dict):
        raise NotImplementedError("Override required")

# === Pandas summary handler ===

class PandasHandler(ProcessEnergyHandler):
    def __init__(self):
        super().__init__()
        
    def summary(self) -> pd.DataFrame:
        """
        Converts the energy samples into a Pandas DataFrame,
        """
        if not self.samples:
            return pd.DataFrame()
        
        data = [{
            "id": sample.id,
            "pid": sample.pid,
            "cpu_percent": sample.cpu_percent,
            "energy_uj": sample.energy
        } for sample in self.samples]

        df = pd.DataFrame(data)
        return df
    
# === CSV summary handler ===

class CSVHandler(ProcessEnergyHandler):
    def __init__(self, filename: str = "energyconsumption.csv"):
        super().__init__()
        self.filename = filename

    def summary(self) -> bool:
        """
        Writes the energy consumption summary to a CSV file.
        """
        if not self.samples:
            return False
        
        with open(self.filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["id", "pid", "cpu_percent", "energy_uj"])
            for sample in self.samples:
                writer.writerow([sample.id, sample.pid, sample.cpu_percent, sample.energy])

        return True