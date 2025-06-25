from pyJoules.energy_meter import measure_energy
from pyJoules.handler.csv_handler import CSVHandler
from pyJoules.device.rapl_device import RaplPsysDomain
import shlex
import subprocess


args = shlex.split("java -javaagent:/home/pietrofbk/git/joularjx/target/joularjx-3.0.1.jar -jar /home/pietrofbk/git/iv4xr-mbt/target/EvoMBT-1.2.2-jar-with-dependencies.jar -random -Dsut_efsm=examples.traffic_light -Drandom_seed=123456")

from pyJoules.device.rapl_device import RaplPsysDomain

csv_handler = CSVHandler('result.csv')
	
@measure_energy(domains = [RaplPsysDomain(1)], handler=csv_handler)
def foo():
	process = subprocess.Popen(args, shell=False)
	process.wait()

foo()
csv_handler.save_data()