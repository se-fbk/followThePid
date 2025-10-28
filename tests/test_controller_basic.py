from followThePid.controller import FollowThePid

def test_init_creates_components(dummy_device, dummy_cpu, dummy_metrics):
    """
    Test that FollowThePid initializes its components correctly.
    """
    monitor = FollowThePid(cmd="echo hello")
    assert monitor.cmd == "echo hello"
    assert hasattr(monitor, "device")
    assert hasattr(monitor, "cpu")
    assert hasattr(monitor, "metrics")

def test_take_measurement_returns_sample(monkeypatch, dummy_device, dummy_cpu, dummy_metrics):
    """
    Test that _take_measurement returns a MetricSample object.
    """
    from followThePid.controller import FollowThePid
    sample_obj = type("S", (), {})()
    monkeypatch.setattr("followThePid.controller.MetricSample", lambda **kw: sample_obj)
    
    f = FollowThePid(cmd="echo test")
    result = f._take_measurement()
    assert result is sample_obj


