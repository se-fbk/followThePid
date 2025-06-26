import csv
from typing import Dict, List
from datetime import datetime
from handler import ProcessEnergyHandler

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
