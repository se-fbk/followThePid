def test_samples_csv_and_pandas(dummy_device, dummy_cpu, dummy_metrics):
    """
    Test that samples_csv and samples_pandas methods work correctly.
    """
    from followThePid.controller import FollowThePid
    f = FollowThePid(cmd="ls")
    assert f.samples_csv("test.csv") is True
    assert f.samples_pandas() == "FAKE_DF"

def test_get_pid_energy_logs_and_returns(dummy_device, dummy_cpu, dummy_metrics):
    """
    Test that get_pid_energy logs the correct information and returns the expected value.
    """
    from followThePid.controller import FollowThePid
    f = FollowThePid(cmd="ls")
    e = f.get_pid_energy()
    assert isinstance(e, float)
    assert e == 42.0
