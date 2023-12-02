from utils import script_path

from processing_r.processing.algorithm import RAlgorithm


def test_can_run():
    alg = RAlgorithm(description_file=script_path("test_algorithm_1.rsx"))
    alg.initAlgorithm()

    assert alg.canExecute()
