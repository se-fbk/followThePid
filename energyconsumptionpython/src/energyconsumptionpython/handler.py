from typing import Dict
from datetime import datetime

class ProcessEnergySample:
    def __init__(self, id: int, pid: int, cpu_percent: float):
        self.id = id
        self.pid = pid
        self.cpu_percent = cpu_percent

class ProcessEnergyHandler:
    """Classe base per handler di misurazioni energetiche"""
    def handle(self, sample: ProcessEnergySample):
        raise NotImplementedError("Override required")

    def handle_summary(self, summary: Dict):
        raise NotImplementedError("Override required")
