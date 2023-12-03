from qgis.core import QgsProcessingContext, QgsProcessingFeedback
from utils import script_path

from processing_r.processing.algorithm import RAlgorithm


def test_can_run():
    alg = RAlgorithm(description_file=script_path("test_algorithm_1.rsx"))
    alg.initAlgorithm()

    assert alg.canExecute()


def test_process():
    alg = RAlgorithm(description_file=script_path("test_input_point.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    result = alg.processAlgorithm({"point": "20.219926,49.138354 [EPSG:4326]"}, context, feedback)

    assert result == {}
