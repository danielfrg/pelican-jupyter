def test_import():
    import pelican_jupyter

    assert pelican_jupyter.__version__ is not None
    assert pelican_jupyter.__version__ != "0.0.0"
    assert len(pelican_jupyter.__version__) > 0
