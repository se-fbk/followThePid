import numpy as np
import time

def test(peak_interval=10, peak_duration=2):
    last_peak = time.time()

    while True:
        now = time.time()
        in_peak = (now - last_peak) < peak_duration
        print(f"now - last_peak {now - last_peak}")
        if in_peak:
            print("Peak")
            for _ in range(5): 
                a = np.random.rand(3500, 3500)
                b = np.random.rand(3500, 3500)
                c = np.dot(a, b)
        else:
            print("NO Peak")
            a = np.random.rand(300, 300)
            b = np.random.rand(300, 300)
            c = np.dot(a, b)
            time.sleep(2)

        if not in_peak: # and (now - last_peak) >= peak_interval:
            last_peak =  time.time()

if __name__ == "__main__":
    test()
