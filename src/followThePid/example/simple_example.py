import time
import math
import random

def heavy_computation():
    print("High CPU load...")
    for _ in range(100_000):
        [math.sqrt(i ** 2 + math.sin(i)) for i in range(500)]

def medium_computation():
    print("Medium CPU load...")
    for _ in range(50_000):
        sum([i * i for i in range(200)])

def light_computation():
    print("Low CPU load (simulating I/O wait)...")
    time.sleep(1)

def simulate_work():
    phases = [
        heavy_computation,
        medium_computation,
        light_computation,
        medium_computation,
        heavy_computation,
    ]

    print("Starting variable workload simulation...")

    for phase in phases:
        phase()
        # Small random delay between phases
        time.sleep(random.uniform(0.1, 0.3))

    print("Simulation finished.")

if __name__ == "__main__":
    simulate_work()
