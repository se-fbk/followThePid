def test_import_package():
    import followThePid
    assert hasattr(followThePid, "__version__")

def test_import_public_symbol():
    from followThePid import FollowThePid
    assert FollowThePid is not None
