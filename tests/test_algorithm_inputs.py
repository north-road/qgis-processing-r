import pytest
from qgis.core import QgsProcessing, QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer
from qgis.PyQt.QtCore import QDate, QDateTime, QTime
from qgis.PyQt.QtGui import QColor

from processing_r.processing.algorithm import RAlgorithm
from tests.utils import IS_API_BELOW_31000, IS_API_BELOW_31400, USE_API_30900, data_path, script_path


def test_simple_inputs():
    """
    Test creation of script with algorithm inputs
    """
    alg = RAlgorithm(description_file=script_path("test_algorithm_2.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    # enum evaluation
    script = alg.build_import_commands({"in_enum": 0}, context, feedback)
    assert "in_enum <- 0" in script

    # boolean evaluation
    script = alg.build_import_commands({"in_bool": True}, context, feedback)
    assert "in_bool <- TRUE" in script

    script = alg.build_import_commands({"in_bool": False}, context, feedback)
    assert "in_bool <- FALSE" in script

    # number evaluation
    script = alg.build_import_commands({"in_number": None}, context, feedback)
    assert "in_number <- NULL" in script

    script = alg.build_import_commands({"in_number": 5}, context, feedback)
    assert "in_number <- 5.0" in script

    script = alg.build_import_commands({"in_number": 5.5}, context, feedback)
    assert "in_number <- 5.5" in script

    script = alg.build_import_commands({"in_string": "some string"}, context, feedback)
    assert 'in_string <- "some string"' in script


def test_folder_inputs():
    """
    Test creation of script with algorithm inputs
    """
    alg = RAlgorithm(description_file=script_path("test_algorithm_2.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    # folder destination
    script = alg.build_import_commands({"param_folder_dest": "/tmp/processing/test_algorithm_2_r/"}, context, feedback)

    # file destination
    script = alg.build_import_commands(
        {"param_html_dest": "/tmp/processing/test_algorithm_2_r/dest.html"}, context, feedback
    )
    assert 'param_html_dest <- "/tmp/processing/test_algorithm_2_r/dest.html"' in script

    script = alg.build_import_commands(
        {"param_file_dest": "/tmp/processing/test_algorithm_2_r/dest.file"}, context, feedback
    )
    assert 'param_file_dest <- "/tmp/processing/test_algorithm_2_r/dest.file"' in script

    script = alg.build_import_commands(
        {"param_csv_dest": "/tmp/processing/test_algorithm_2_r/dest.csv"}, context, feedback
    )
    assert 'param_csv_dest <- "/tmp/processing/test_algorithm_2_r/dest.csv"' in script


def test_read_sf():
    """
    Test reading vector inputs
    """
    alg = RAlgorithm(description_file=script_path("test_vectorin.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()
    script = alg.build_import_commands({"Layer": data_path("lines.shp")}, context, feedback)

    if USE_API_30900:
        assert script[0] == 'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(
            data_path("lines.shp")
        )
    else:
        assert script[0] == 'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(
            data_path("lines.shp")
        )

    script = alg.build_import_commands({"Layer": data_path("lines.shp").replace("/", "\\")}, context, feedback)
    if USE_API_30900:
        assert script[0] == 'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(
            data_path("lines.shp")
        )
    else:
        assert script[0] == 'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(
            data_path("lines.shp")
        )

    vl = QgsVectorLayer(data_path("test_gpkg.gpkg") + "|layername=points")
    assert vl.isValid()

    vl2 = QgsVectorLayer(data_path("test_gpkg.gpkg") + "|layername=lines")
    assert vl2.isValid()

    script = alg.build_import_commands({"Layer": vl, "Layer2": vl2}, context, feedback)

    if USE_API_30900:
        # use the newer api and avoid unnecessary layer translation
        assert script == [
            'Layer <- st_read("{}", layer = "points", quiet = TRUE, stringsAsFactors = FALSE)'.format(
                data_path("test_gpkg.gpkg")
            ),
            'Layer2 <- st_read("{}", layer = "lines", quiet = TRUE, stringsAsFactors = FALSE)'.format(
                data_path("test_gpkg.gpkg")
            ),
        ]
    else:
        # older version, forced to use inefficient api
        assert 'Layer <- st_read("/tmp' == script[0]
        assert 'Layer2 <- st_read("/tmp' == script[1]


def test_read_raster():
    """
    Test reading raster inputs
    """
    alg = RAlgorithm(description_file=script_path("test_raster_in_out.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    script = alg.build_import_commands({"Layer": data_path("dem.tif")}, context, feedback)
    assert 'Layer <- brick("{}")'.format(data_path("dem.tif")) in script

    script = alg.build_import_commands({"Layer": data_path("dem.tif").replace("/", "\\")}, context, feedback)
    assert 'Layer <- brick("{}")'.format(data_path("dem.tif")) in script

    script = alg.build_import_commands({"Layer": None}, context, feedback)
    assert "Layer <- NULL" in script

    alg = RAlgorithm(description_file=script_path("test_rasterin_names.rsx"))
    alg.initAlgorithm()

    script = alg.build_import_commands({"Layer": data_path("dem.tif")}, context, feedback)
    assert 'Layer <- "{}"'.format(data_path("dem.tif")) in script

    script = alg.build_import_commands({"Layer": None}, context, feedback)
    assert "Layer <- NULL" in script


def test_read_multi_raster():
    """
    Test raster multilayer input parameter
    """
    alg = RAlgorithm(description_file=script_path("test_multirasterin.rsx"))
    alg.initAlgorithm()

    raster_param = alg.parameterDefinition("Layer")
    assert raster_param.type() == "multilayer"
    assert raster_param.layerType() == QgsProcessing.TypeRaster

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()
    script = alg.build_import_commands(
        {"Layer": [data_path("dem.tif"), data_path("dem2.tif")]},
        context,
        feedback,
    )

    assert script == [
        'tempvar0 <- brick("{}")'.format(data_path("dem.tif")),
        'tempvar1 <- brick("{}")'.format(data_path("dem2.tif")),
        "Layer = list(tempvar0,tempvar1)",
    ]

    script = alg.build_import_commands({"Layer": []}, context, feedback)
    assert script == ["Layer = list()"]


def test_read_multi_vector():
    """
    Test vector multilayer input parameter
    """
    alg = RAlgorithm(description_file=script_path("test_multivectorin.rsx"))
    alg.initAlgorithm()

    param = alg.parameterDefinition("Layer")
    assert param.type() == "multilayer"
    assert param.layerType() == QgsProcessing.TypeVectorAnyGeometry

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    script = alg.build_import_commands(
        {"Layer": [data_path("lines.shp"), data_path("points.gml")]},
        context,
        feedback,
    )

    assert script == [
        'tempvar0 <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(data_path("lines.shp")),
        'tempvar1 <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(data_path("points.gml")),
        "Layer = list(tempvar0,tempvar1)",
    ]

    script = alg.build_import_commands({"Layer": []}, context, feedback)
    assert script == ["Layer = list()"]


def test_multi_field():
    """
    Test multiple field input parameter
    """
    alg = RAlgorithm(description_file=script_path("test_field_multiple.rsx"))
    alg.initAlgorithm()

    param = alg.parameterDefinition("MultiField")
    assert param.type() == "field"
    assert param.allowMultiple() is True

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    script = alg.build_import_commands({"Layer": data_path("lines.shp")}, context, feedback)

    assert script == [
        'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(data_path("lines.shp")),
        "MultiField <- NULL",
    ]

    script = alg.build_import_commands({"Layer": data_path("lines.shp"), "MultiField": ["a"]}, context, feedback)
    assert script == [
        'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(data_path("lines.shp")),
        'MultiField <- c("a")',
    ]

    script = alg.build_import_commands({"Layer": data_path("lines.shp"), "MultiField": ["a", 'b"c']}, context, feedback)
    assert script == [
        'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(data_path("lines.shp")),
        'MultiField <- c("a","b\\"c")',
    ]


def test_enums():
    """
    Test for both enum types
    """
    alg = RAlgorithm(description_file=script_path("test_enums.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    script = alg.build_import_commands({"enum_normal": 0}, context, feedback)
    assert "enum_normal <- 0" == script[1]

    script = alg.build_import_commands({"enum_string": 0}, context, feedback)
    assert 'enum_string <- "enum_a"' == script[0]


def test_enums_multiple():
    """
    Test for both enum multiple types
    """
    alg = RAlgorithm(description_file=script_path("test_enum_multiple.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    params = {"enum_normal": [0, 1], "enum_string": [0, 1], "R_CONSOLE_OUTPUT": "TEMPORARY_OUTPUT"}
    script = alg.build_import_commands(params, context, feedback)

    assert "enum_normal <- c(0, 1)" in script
    assert 'enum_string <- c("enum_a","enum_b")' in script
    assert "enum_string_optional <- NULL" in script
    assert "enum_normal_optional <- NULL" in script

    params = {
        "enum_normal": [0, 1, 2],
        "enum_string": [0, 2],
        "enum_string_optional": [0],
        "enum_normal_optional": [1],
        "R_CONSOLE_OUTPUT": "TEMPORARY_OUTPUT",
    }
    script = alg.build_import_commands(params, context, feedback)

    assert "enum_normal <- c(0, 1, 2)" in script
    assert 'enum_string <- c("enum_a","enum_c")' in script
    assert 'enum_string_optional <- c("enum_a")' in script
    assert "enum_normal_optional <- c(1)" in script


def test_point():
    """
    Test Point parameter
    """

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    alg = RAlgorithm(description_file=script_path("test_input_point.rsx"))
    alg.initAlgorithm()

    script = alg.build_r_script({"point": "20.219926,49.138354 [EPSG:4326]"}, context, feedback)

    assert 'library("sf")' in script
    assert "point <- st_sfc(st_point(c(20.219926,49.138354)), crs = point_crs)" in script


def test_range():
    """
    Test range parameter
    """

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    alg = RAlgorithm(description_file=script_path("test_input_range.rsx"))
    alg.initAlgorithm()

    script = alg.build_r_script({"range": [0, 1]}, context, feedback)
    assert "range <- c(min = 0.0, max = 1.0)" in script

    script = alg.build_r_script({"range": [5, 10]}, context, feedback)
    assert "range <- c(min = 5.0, max = 10.0)" in script

    script = alg.build_r_script({"range": [0.5, 1.5]}, context, feedback)
    assert "range <- c(min = 0.5, max = 1.5)" in script


def test_color():
    """
    Test color parameter
    """

    if IS_API_BELOW_31000:
        pytest.skip("QGIS version does not support this.")

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    alg = RAlgorithm(description_file=script_path("test_input_color.rsx"))
    alg.initAlgorithm()

    script = alg.build_r_script({"color": QColor(0, 255, 0)}, context, feedback)
    assert "color <- rgb(0, 255, 0, 255, maxColorValue = 255)" in script

    script = alg.build_r_script({"color": QColor(255, 0, 0)}, context, feedback)
    assert "color <- rgb(255, 0, 0, 255, maxColorValue = 255)" in script


def test_date_time():
    """
    Test datetime parameter
    """

    if IS_API_BELOW_31400:
        pytest.skip("QGIS version does not support this.")

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    alg = RAlgorithm(description_file=script_path("test_input_datetime.rsx"))
    alg.initAlgorithm()

    script = alg.build_r_script({"datetime": QDateTime(QDate(2021, 10, 1), QTime(16, 57, 0))}, context, feedback)
    assert 'datetime <- as.POSIXct("2021-10-01T16:57:00", format = "%Y-%m-%dT%H:%M:%S")' in script

    script = alg.build_r_script({"datetime": QDateTime(QDate(2021, 10, 14), QTime(14, 48, 52))}, context, feedback)
    assert 'datetime <- as.POSIXct("2021-10-14T14:48:52", format = "%Y-%m-%dT%H:%M:%S")' in script


def test_expressions():
    """
    Test Expression parameter
    """

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    alg = RAlgorithm(description_file=script_path("test_input_expression.rsx"))
    alg.initAlgorithm()

    script = alg.build_r_script({""}, context, feedback)

    assert "number <- 6" in script
    assert any(['geometry <- sf::st_as_sfc("Polygon ' in line for line in script])  # pylint: disable=use-a-generator

    assert 'date_a <- as.POSIXct("2020-05-04", format = "%Y-%m-%d")' in script
    assert 'time_a <- lubridate::hms("13:45:30")' in script


def test_raster_band():
    """
    Test datetime parameter
    """

    alg = RAlgorithm(description_file=script_path("test_raster_band.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    script = alg.build_import_commands({"Band": 1, "Layer": data_path("dem.tif")}, context, feedback)
    assert "Band <- 1" in script
