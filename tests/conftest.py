from pathlib import Path

import pytest
from qgis.PyQt.QtCore import QCoreApplication, QSettings

from processing_r.processing.provider import RAlgorithmProvider


@pytest.fixture
def data_folder() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(autouse=True, scope="session")
def setup_plugin():
    QCoreApplication.setOrganizationName("North Road")
    QCoreApplication.setOrganizationDomain("qgis.org")
    QCoreApplication.setApplicationName("QGIS-R")
    QSettings().clear()


@pytest.fixture(autouse=True, scope="session")
def plugin_provider(setup_plugin) -> RAlgorithmProvider:
    provider = RAlgorithmProvider()
    provider.load()
    return provider
