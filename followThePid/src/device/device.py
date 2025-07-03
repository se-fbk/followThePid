import sys
from .linux import DeviceLinux

class Device:
    def __new__(cls):
        current_platform = sys.platform
        
        if current_platform.startswith('win'):
            return None
        elif current_platform.startswith('linux'):
            return DeviceLinux()
        elif current_platform.startswith('darwin'):
            return None
        else:
            raise NotImplementedError(f"Platform {current_platform} not supported.")