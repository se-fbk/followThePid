import os 
def detect_sockets():
    """
    Detects available physical sockets (NUMA nodes) from /sys.

    Returns:
        List[int]: List of socket IDs (typically [0, 1, ...]).
    """
    sockets = set()
    CPU_BASE_PATH = "/sys/devices/system/cpu/"

    for cpu in os.listdir(CPU_BASE_PATH):
        if cpu.startswith("cpu") and cpu[3:].isdigit():
            cpu_id = cpu[3:]
            try:
                with open(f"{CPU_BASE_PATH}/cpu{cpu_id}/topology/physical_package_id") as f:
                    socket_id = int(f.read().strip())
                    sockets.add(socket_id)
            except FileNotFoundError:
                continue

    return sorted(sockets)
