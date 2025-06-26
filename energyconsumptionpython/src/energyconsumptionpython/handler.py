from typing import Dict
from datetime import datetime

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
