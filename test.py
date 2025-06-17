import psutil
import time
import subprocess
import sys
from pyJoules.energy_meter import EnergyMeter
from pyJoules.device.rapl_device import RaplDevice, RaplPackageDomain
from pyJoules.device.device_factory import DeviceFactory

def monitor_process(pid):
    process = psutil.Process(pid)

    domains = [RaplPackageDomain(0)]
    devices = DeviceFactory.create_devices(domains)
    meter = EnergyMeter(devices)

    print(f"\nMonitoraggio energia per PID {pid}... Premi CTRL+C per uscire.")
    process.cpu_percent(interval=0.1)  # Warm-up

    totale_stima = 0.0  # Energia stimata per il processo (µJ)
    totale_rapl = 0.0    # Energia totale letta da RAPL (µJ)

    try:
        while True:
            meter.start()
            time.sleep(1)
            meter.stop()

            energy_data = meter.get_trace()
            if not energy_data:
                print("Nessuna misurazione energetica registrata.")
                continue

            last = energy_data[-1]
            energy_by_domain = last.energy  #{'package_0': 123456}
            energia_rapl_int = sum(energy_by_domain.values())  # Energia totale misurata (µJ)
            totale_rapl += energia_rapl_int

            num_cores = psutil.cpu_count(logical=True) or 1
            cpu_percent = (process.cpu_percent(interval=None) / 100) / num_cores

            energia_stima = energia_rapl_int * (cpu_percent / 100)
            totale_stima += energia_stima

            print(
                f"PID {pid} | "
                f"CPU: {cpu_percent:.1f}% | "
                #f"CPU/n.cores: {cpu_percent / num_cores} | "
                f"Energy: {energia_stima / 1_000_000:.2f} J (curr), "
                f"{totale_stima / 1_000_000:.2f} J (proc total), "
                f"{totale_rapl / 1_000_000:.2f} J (RAPL total)"
            )

    except KeyboardInterrupt:
        print("\nMonitoraggio terminato.")
        print(
            f"\nEnergia totale stimata per PID {pid}: "
            f"{totale_stima:.2f} µJ ({totale_stima / 1_000_000:.6f} J)"
        )
        print(
            f"Energia totale letta da RAPL: "
            f"{totale_rapl:.2f} µJ ({totale_rapl / 1_000_000:.6f} J)"
        )

if __name__ == "__main__":
    # pid = int(input("Inserisci il PID da monitorare: "))
    # monitor_process(pid)

    script_path = "./underTest.py"

    try:
        # Avvia il programma come sottoprocesso
        proc = subprocess.Popen([sys.executable, script_path])
        monitor_process(proc.pid)
    except FileNotFoundError:
        print("Script non trovato.")
    except Exception as e:
        print(f"Errore nell'esecuzione: {e}")
