from pathlib import Path

from qgis.core import Qgis, QgsProcessingAlgorithm


def script_path(filename: str) -> str:
    path = Path(__file__).parent / "scripts" / filename
    return path.as_posix()


def data_path(filename: str) -> str:
    path = Path(__file__).parent / "data" / filename
    return path.as_posix()


USE_API_30900 = Qgis.QGIS_VERSION_INT >= 30900 and hasattr(
    QgsProcessingAlgorithm, "parameterAsCompatibleSourceLayerPathAndLayerName"
)

IS_API_BELOW_31000 = Qgis.QGIS_VERSION_INT < 31000

IS_API_BELOW_31400 = Qgis.QGIS_VERSION_INT < 31400

IS_API_ABOVE_31604 = Qgis.QGIS_VERSION_INT >= 31604
