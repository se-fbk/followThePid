import followThePid as ft

def test_all_contains_expected_symbols():
    """
    Test that the __all__ variable in followThePid contains the expected public symbols.
    """
    assert "FollowThePid" in ft.__all__
