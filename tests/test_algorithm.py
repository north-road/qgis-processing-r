from pathlib import Path

import processing
from utils import data_path, script_path

from processing_r.processing.algorithm import RAlgorithm


def test_can_run():
    alg = RAlgorithm(description_file=script_path("test_algorithm_1.rsx"))
    alg.initAlgorithm()

    assert alg.canExecute()


def test_run_point():
    result = processing.run("r:testpointinput", {"point": "20.219926,49.138354 [EPSG:4326]"})

    assert result == {}


def test_run_raster_creation():
    result = processing.run("r:rasterinout", {"Layer": data_path("dem.tif"), "out_raster": "TEMPORARY_OUTPUT"})

    assert "out_raster" in result.keys()
    assert Path(result["out_raster"]).exists()


def test_run_enums():
    result = processing.run("r:testenumstypemultiple", {"enum_normal": 0, "enum_string": 1})

    print(result)
    print(result.keys())
    assert "R_CONSOLE_OUTPUT" in result.keys()
    assert Path(result["R_CONSOLE_OUTPUT"]).exists()


def test_run_graphs():
    result = processing.run(
        "r:graphs",
        {
            "RPLOTS": "TEMPORARY_OUTPUT",
            "Layer": data_path("points.gml"),
            "Field": "id",
        },
    )

    assert "RPLOTS" in result.keys()
    assert Path(result["RPLOTS"]).exists()
