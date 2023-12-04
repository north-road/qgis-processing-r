from qgis.core import QgsProcessingContext, QgsProcessingFeedback
from utils import data_path, script_path

from processing_r.processing.algorithm import RAlgorithm


def test_can_run():
    alg = RAlgorithm(description_file=script_path("test_algorithm_1.rsx"))
    alg.initAlgorithm()

    assert alg.canExecute()


def test_process_1():
    alg = RAlgorithm(description_file=script_path("test_input_point.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    result = alg.processAlgorithm({"point": "20.219926,49.138354 [EPSG:4326]"}, context, feedback)

    assert result == {}


def test_process_2():
    alg = RAlgorithm(description_file=script_path("test_enum_multiple.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    result = alg.processAlgorithm({"enum_normal": 0, "enum_string": 1}, context, feedback)

    assert result == {}


def test_process_3():
    alg = RAlgorithm(description_file=script_path("test_plots.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    result = alg.processAlgorithm({"Layer": data_path("points.gml"), "Field": "id"}, context, feedback)

    print(result)

    assert "RPLOTS" in result.keys()
