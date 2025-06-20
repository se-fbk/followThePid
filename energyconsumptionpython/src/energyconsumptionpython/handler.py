from typing import Dict
from datetime import datetime

class ProcessEnergySample:
    def __init__(self, timestamp: datetime, pid: int, cpu_percent: float, process_energy: float, rapl_energy: float):
        self.timestamp = timestamp
        self.pid = pid
        self.cpu_percent = cpu_percent
        self.process_energy = process_energy
        self.rapl_energy = rapl_energy

class ProcessEnergyHandler:
    """Classe base per handler di misurazioni energetiche"""
    def handle(self, sample: ProcessEnergySample):
        raise NotImplementedError("Override required")

    def handle_summary(self, summary: Dict):
        raise NotImplementedError("Override required")
