from pathlib import Path

import pytest
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QCoreApplication, QSettings

from processing_r.processing.provider import RAlgorithmProvider
from processing_r.processing.utils import RUtils


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
def plugin_provider(setup_plugin, qgis_processing) -> RAlgorithmProvider:
    provider = RAlgorithmProvider()

    QgsApplication.processingRegistry().addProvider(provider)

    test_scripts_path = Path(__file__).parent / "scripts"
    scripts_paths = ProcessingConfig.getSetting(RUtils.RSCRIPTS_FOLDER) + ";" + test_scripts_path.as_posix()

    ProcessingConfig.setSettingValue(RUtils.RSCRIPTS_FOLDER, scripts_paths)

    provider.loadAlgorithms()

    return provider
