import csv
from typing import Dict
from handler import ProcessEnergyHandler, ProcessEnergySample

class CSVHandler(ProcessEnergyHandler):
    def __init__(self, log_filename: str = "energy_log.csv", summary_filename: str = "energy_summary.csv"):
        self.log_filename = log_filename
        self.summary_filename = summary_filename

        with open(self.log_filename, 'w', newline='') as log_file:
            writer = csv.writer(log_file)
            writer.writerow(['PID', 'Timestamp', 'CPU (%)', 'Process Energy (uJ)', 'RAPL Energy (uJ)'])

        with open(self.summary_filename, 'w', newline='') as summary_file:
            writer = csv.writer(summary_file)
            writer.writerow(['Metric', 'Value'])

    def handle(self, sample: ProcessEnergySample):
        with open(self.log_filename, 'a', newline='') as log_file:
            writer = csv.writer(log_file)
            writer.writerow([
                sample.pid,
                sample.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                round(sample.cpu_percent, 2),
                round(sample.process_energy, 2),
                round(sample.rapl_energy, 2)
            ])

    def handle_summary(self, summary: Dict):
        with open(self.summary_filename, 'a', newline='') as summary_file:
            writer = csv.writer(summary_file)
            for key, value in summary.items():
                writer.writerow([key, value])
