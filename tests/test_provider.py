from processing_r.processing.provider import RAlgorithmProvider


def test_provider():
    provider = RAlgorithmProvider()

    assert provider.name() == "R"
    assert provider.id() == "r"
    assert provider.versionInfo()
    assert "QGIS R Provider version " in provider.versionInfo()
