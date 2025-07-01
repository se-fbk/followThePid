# followThePid

**followThePid** is a Python library for tracing the **CPU usage** and **energy consumption** of a running process using its PID.  It uses **Intel RAPL** interfaces (via [`pyJoules`](https://github.com/powerapi-ng/pyJoules)) and [`psutil`](https://github.com/giampaolo/psutil) to follow a process and all its children, collecting fine-grained energy and performance metrics over time.

---

## Features

- Trace CPU usage and energy per sampling interval
- Option to normalize CPU usage per core (iris mode)
- Uses Intel RAPL (via `pyJoules`) for energy measurements
- Built-in support for saving data as:
  - CSV file
  - Pandas DataFrame
---

## Requirements
- Python 3.12+
- Linux system with Intel RAPL support (Intel CPU required)
- sudo/root privileges (in some environments)


## Installation
```bash
git clone https://github.com/your-username/followThePid.git
cd followThePid
pip install -r followThePid/requirements.txt
```

## RAPL Permissions
By default, **on recent kernels (≥ 5.10)**, access is **restricted to root**, as a security mitigation. To allow non-root reads:
```bash
# Example Package 0
sudo chmod o+r /sys/class/powercap/intel-rapl:0/energy_uj 
```


## Usage
```python
from followthepid.monitor import FollowThePid
from pyJoules.device.rapl_device import RaplPackageDomain
from followthepid.handlers import PandasHandler

handler = PandasHandler()
monitor = FollowThePid(
    cmd="python my_script.py",
    domains=[RaplPackageDomain(0)],  # adjust depending on your hardware
    sampling_interval=0.1,
    irix_mode=True,
    handler=handler
)

monitor.monitor()

# Access results
df = handler.summary()
print(df)

```
