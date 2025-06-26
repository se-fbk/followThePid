import pandas as pd
from handler import ProcessEnergyHandler

class PandasHandler(ProcessEnergyHandler):
    def __init__(self):
        super().__init__()
        
    def summary(self) -> pd.DataFrame:
        """
        Converts the energy samples into a Pandas DataFrame,
        """
        if not self.samples:
            return pd.DataFrame()
        
        data = [{
            "id": sample.id,
            "pid": sample.pid,
            "cpu_percent": sample.cpu_percent,
            "energy_uj": sample.energy
        } for sample in self.samples]

        df = pd.DataFrame(data)
        return df
