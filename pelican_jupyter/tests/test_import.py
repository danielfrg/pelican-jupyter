def test_import():
    import pelican_jupyter

    assert pelican_jupyter.__version__ is not None
    assert pelican_jupyter.__version__ != "0.0.0"
    assert len(pelican_jupyter.__version__) > 0


def test_import_markup():
    from pelican_jupyter import markup as nb_markup

    assert nb_markup


def test_import_liquid():
    from pelican_jupyter import liquid as nb_liquid

    assert nb_liquid
