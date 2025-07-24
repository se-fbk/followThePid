import sys
from .linux import DeviceLinux
from .mac import DeviceMacOS
# from .windows import DeviceWindows

class Device:
    def __new__(cls, sampling_interval: float = 0.1):

        current_platform = sys.platform
        
        if current_platform.startswith('linux'):
            return DeviceLinux(sampling_interval)
        
        elif current_platform.startswith('win'):
            # return DeviceWindows(sampling_interval)
            raise NotImplementedError("Windows is not yet supported.")
        
        elif current_platform.startswith('darwin'):
            return DeviceMacOS(sampling_interval)
        
        else:
            raise RuntimeError(f"Unsupported platform: {current_platform}. Supported platforms are Linux, Windows, and macOS.")