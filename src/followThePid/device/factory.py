import sys, subprocess, logging
from .linux import DeviceLinux
from .mac import DeviceMacOS
# from .windows import DeviceWindows

class Device:
    def __new__(cls, sampling_interval: float = 0.1):

        current_platform = sys.platform
        sockets = get_num_sockets()
          
        if current_platform.startswith('linux'):
            logging.info(f"Detected Linux platform with {sockets} sockets.")
            return DeviceLinux(sampling_interval, sockets=sockets)
        
        elif current_platform.startswith('win'):
            # return DeviceWindows(sampling_interval)
            logging.info(f"Detected Windows platform with {sockets} sockets.")
            raise NotImplementedError("Windows is not yet supported.")
        
        elif current_platform.startswith('darwin'):
            logging.info(f"Detected MacOS platform with {sockets} sockets.")
            return DeviceMacOS(sampling_interval)
        
        else:
            raise RuntimeError(f"Unsupported platform: {current_platform}. Supported platforms are Linux, Windows, and macOS.")
        


def get_num_sockets():
    """
    Returns the number of CPU sockets on the system.
    """
    sockets = 1

    try:
        result = subprocess.run(
            ["lscpu"], capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith("Socket(s):"):
                sockets = int(line.split(":")[1].strip())             
                return sockets
    except Exception:
        pass

    return sockets
