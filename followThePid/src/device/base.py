from abc import ABC, abstractmethod

class DeviceBase(ABC):
    def __init__(self, sampling_interval: float):
        self.sampling_interval = sampling_interval

    @abstractmethod
    def setup(self):
        pass
    
    @abstractmethod
    def get_energy(self):
        pass

    @abstractmethod
    def close(self):
        pass

