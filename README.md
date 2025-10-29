# followThePid

**followThePid** is a Python library for tracing the **CPU usage** and **energy consumption** of a running process using its PID.
It supports **Linux** and **macOS** (Intel and Apple Silicon).

---

## Features

- Trace CPU usage and energy per sampling interval
- Option to normalize CPU usage per core (iris mode)
- Uses `Intel RAPL` and `powermetrics` for energy measurements
- Built-in support for saving data as:
  - CSV file
  - Pandas DataFrame
---

## Requirements
- Python 3.12+
- One of:
  - Linux with Intel CPU and RAPL support
  - macOS with Intel CPU or Apple Silicon (M1/M2/M3)
- sudo/root privileges


## Installation
```bash
git clone https://github.com/your-username/followThePid.git
cd followThePid
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## RAPL Permissions

### Linux (Intel CPUs)
By default, **on recent kernels (≥ 5.10)**, access is **restricted to root**, as a security mitigation. To allow non-root reads:
```bash
# Example Package 0
sudo chmod o+r /sys/class/powercap/intel-rapl:0/energy_uj 
```

### macOS (Intel and M-series)
Energy estimation rely on `powermetrics APIs` , sudo is needed.


## Usage
```python
import followThePid 
monitor = FollowThePid(
    cmd="python my_script.py",

)

# Start monitoring the process
monitor.monitor() 

# Summary
monitor.samples_csv()
```

## Learn More

For detailed information on how **followThePid** works, supported architectures, and configuration examples,  
see the [📘 Wiki](https://github.com/se-fbk/followThePid/wiki/FollowThePid).
