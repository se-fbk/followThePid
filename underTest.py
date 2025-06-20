import numpy as np
import time

def test(peak_interval=10, peak_duration=2, num_peaks=2):
    last_peak = time.time()
    peak_count = 0

    while peak_count < num_peaks:
        now = time.time()
        in_peak = (now - last_peak) < peak_duration
        print(f"now - last_peak {now - last_peak:.2f}")
        
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

            # Dopo un periodo "no peak", se è ora di ripartire con un picco, lo facciamo
            if (now - last_peak) >= peak_interval:
                last_peak = time.time()
                peak_count += 1  # Avanzamento del contatore di picchi

    print("Test completato.")


if __name__ == "__main__":
    #print PID
    import os
    pid = os.getpid()
    print(f"PID: {pid}")
    #sleep 5 secondi
    time.sleep(10)
    test()
