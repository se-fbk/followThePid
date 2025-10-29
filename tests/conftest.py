import pytest
import types

@pytest.fixture
def dummy_device(monkeypatch):
    """Device mock"""
    dummy = types.SimpleNamespace()
    dummy.get_energy = lambda: 123.456
    dummy.close = lambda: None
    monkeypatch.setattr("followThePid.controller.Device", lambda *a, **k: dummy)
    return dummy

@pytest.fixture
def dummy_cpu(monkeypatch):
    """CPUManager mock"""
    cpu = types.SimpleNamespace()
    cpu.get_cpu_usage = lambda: 0.5
    cpu.get_cpu_system = lambda: 0.25
    cpu.get_process_tree = lambda: []
    cpu.set_pid = lambda pid: None
    cpu.get_pid = lambda: 1234
    monkeypatch.setattr("followThePid.controller.CPUManager", lambda *a, **k: cpu)
    return cpu

@pytest.fixture
def dummy_metrics(monkeypatch):
    """MetricsHandler mock"""
    m = types.SimpleNamespace()
    m.add_sample = lambda s: True
    m.samples_csv = lambda f="": True
    m.samples_pandas = lambda: "FAKE_DF"
    m.get_pid_energy = lambda: 42.0
    monkeypatch.setattr("followThePid.controller.MetricsHandler", lambda *a, **k: m)
    return m
