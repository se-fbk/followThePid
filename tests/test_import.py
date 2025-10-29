def test_import_package():
    """
    Test that the followThePid package can be imported.
    """
    import followThePid
    assert hasattr(followThePid, "__version__")

def test_import_public_symbol():
    """
    Test that the FollowThePid class can be imported from the public API.
    """
    from followThePid import FollowThePid
    assert FollowThePid is not None
