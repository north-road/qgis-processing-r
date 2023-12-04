from qgis.core import (
    QgsProcessing,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsRasterLayer,
    QgsVectorLayer,
)

from processing_r.processing.algorithm import RAlgorithm
from tests.utils import USE_API_30900, data_path, script_path


def test_vector_outputs():
    """
    Test writing vector outputs
    """
    alg = RAlgorithm(description_file=script_path("test_vectorout.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    script = alg.build_export_commands(
        {"Output": "/home/test/lines.shp", "OutputCSV": "/home/test/tab.csv"}, context, feedback
    )
    assert script == [
        'st_write(Output, "/home/test/lines.shp", layer = "lines", quiet = TRUE)',
        'write.csv(OutputCSV, "/home/test/tab.csv", row.names = FALSE)',
    ]

    script = alg.build_export_commands(
        {"Output": "/home/test/lines.gpkg", "OutputCSV": "/home/test/tab.csv"}, context, feedback
    )
    assert script == [
        'st_write(Output, "/home/test/lines.gpkg", layer = "lines", quiet = TRUE)',
        'write.csv(OutputCSV, "/home/test/tab.csv", row.names = FALSE)',
    ]


def test_multi_outputs():
    """
    Test writing vector outputs
    """
    alg = RAlgorithm(description_file=script_path("test_multiout.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    script = alg.build_export_commands(
        {"Output": "/home/test/lines.shp", "OutputCSV": "/home/test/tab.csv", "OutputFile": "/home/test/file.csv"},
        context,
        feedback,
    )

    assert 'st_write(Output, "/home/test/lines.shp", layer = "lines", quiet = TRUE)' in script
    assert 'write.csv(OutputCSV, "/home/test/tab.csv", row.names = FALSE)' in script

    assert script[2].startswith('cat("##OutputFile", file=')
    assert script[3].startswith("cat(OutputFile, file=")
    assert script[4].startswith('cat("##OutputNum", file=')
    assert script[5].startswith("cat(OutputNum, file=")
    assert script[6].startswith('cat("##OutputStr", file=')
    assert script[7].startswith("cat(OutputStr, file=")


def test_raster_output():
    """
    Test writing raster outputs
    """
    alg = RAlgorithm(description_file=script_path("test_raster_in_out.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    script = alg.build_export_commands(
        {"Layer": data_path("dem.tif"), "out_raster": "/tmp/raster.tif"},
        context,
        feedback,
    )

    assert 'writeRaster(out_raster, "/tmp/raster.tif", overwrite = TRUE)' in script
