from qgis.core import QgsProcessing, QgsProcessingParameterFile, QgsProcessingParameterNumber

from processing_r.processing.algorithm import RAlgorithm
from tests.utils import script_path


def test_script_parsing_1():
    """
    Test script file parsing
    """
    alg = RAlgorithm(description_file=script_path("test_algorithm_1.rsx"))
    alg.initAlgorithm()

    assert alg.error is None
    assert alg.name() == "test_algorithm_1"
    assert alg.displayName() == "test algorithm 1"
    assert "test_algorithm_1.rsx" in alg.description_file
    assert alg.show_plots is True
    assert alg.pass_file_names is True
    assert alg.show_console_output is False


def test_script_parsing_2():
    """
    Test script file parsing
    """
    alg = RAlgorithm(description_file=script_path("test_algorithm_2.rsx"))
    alg.initAlgorithm()
    assert alg.error is None
    assert alg.name() == "mytest"
    assert alg.displayName() == "my test"
    assert alg.group() == "my group"
    assert alg.groupId() == "my group"
    assert alg.show_plots is False
    assert alg.pass_file_names is False
    assert alg.show_console_output is False

    # test that inputs were created correctly
    raster_param = alg.parameterDefinition("in_raster")
    assert raster_param.type() == "raster"

    vector_param = alg.parameterDefinition("in_vector")
    assert vector_param.type() == "source"

    field_param = alg.parameterDefinition("in_field")
    assert field_param.type() == "field"
    assert field_param.parentLayerParameterName() == "in_vector"

    extent_param = alg.parameterDefinition("in_extent")
    assert extent_param.type() == "extent"

    string_param = alg.parameterDefinition("in_string")
    assert string_param.type() == "string"

    file_param = alg.parameterDefinition("in_file")
    assert file_param.type() == "file"

    number_param = alg.parameterDefinition("in_number")
    assert number_param.type() == "number"
    assert number_param.dataType() == QgsProcessingParameterNumber.Double

    enum_param = alg.parameterDefinition("in_enum")
    assert enum_param.type() == "enum"

    enum_param = alg.parameterDefinition("in_enum2")
    assert enum_param.type() == "enum"
    assert enum_param.options() == ["normal", "log10", "ln", "sqrt", "exp"]

    bool_param = alg.parameterDefinition("in_bool")
    assert bool_param.type() == "boolean"

    # outputs
    vector_output = alg.outputDefinition("out_vector")
    assert vector_output.type() == "outputVector"
    assert vector_output.dataType() == QgsProcessing.TypeVectorAnyGeometry

    vector_dest_param = alg.parameterDefinition("param_vector_dest")
    assert vector_dest_param.type() == "vectorDestination"
    assert vector_dest_param.dataType() == QgsProcessing.TypeVectorAnyGeometry

    table_output = alg.outputDefinition("out_table")
    assert table_output.type() == "outputVector"
    assert table_output.dataType() == QgsProcessing.TypeVector

    table_dest_param = alg.parameterDefinition("param_table_dest")
    assert table_dest_param.type() == "vectorDestination"
    assert table_dest_param.dataType() == QgsProcessing.TypeVector

    vector_dest_param = alg.parameterDefinition("param_vector_dest2")
    assert vector_dest_param.type() == "vectorDestination"
    assert vector_dest_param.dataType() == QgsProcessing.TypeVectorAnyGeometry

    vector_dest_param = alg.parameterDefinition("param_vector_point_dest")
    assert vector_dest_param.type() == "vectorDestination"
    assert vector_dest_param.dataType() == QgsProcessing.TypeVectorPoint

    vector_dest_param = alg.parameterDefinition("param_vector_line_dest")
    assert vector_dest_param.type() == "vectorDestination"
    assert vector_dest_param.dataType() == QgsProcessing.TypeVectorLine

    vector_dest_param = alg.parameterDefinition("param_vector_polygon_dest")
    assert vector_dest_param.type() == "vectorDestination"
    assert vector_dest_param.dataType() == QgsProcessing.TypeVectorPolygon

    raster_output = alg.outputDefinition("out_raster")
    assert raster_output.type() == "outputRaster"

    raster_dest_param = alg.parameterDefinition("param_raster_dest")
    assert raster_dest_param.type() == "rasterDestination"

    number_output = alg.outputDefinition("out_number")
    assert number_output.type() == "outputNumber"

    string_output = alg.outputDefinition("out_string")
    assert string_output.type() == "outputString"

    layer_output = alg.outputDefinition("out_layer")
    assert layer_output.type() == "outputLayer"

    folder_output = alg.outputDefinition("out_folder")
    assert folder_output.type() == "outputFolder"

    folder_dest_param = alg.parameterDefinition("param_folder_dest")
    assert folder_dest_param.type() == "folderDestination"

    html_output = alg.outputDefinition("out_html")
    assert html_output.type() == "outputHtml"

    html_dest_param = alg.parameterDefinition("param_html_dest")
    assert html_dest_param.type() == "fileDestination"

    file_output = alg.outputDefinition("out_file")
    assert file_output.type() == "outputFile"

    file_dest_param = alg.parameterDefinition("param_file_dest")
    assert file_dest_param.type() == "fileDestination"

    csv_output = alg.outputDefinition("out_csv")
    assert csv_output.type() == "outputFile"

    csv_dest_param = alg.parameterDefinition("param_csv_dest")
    assert csv_dest_param.type() == "fileDestination"
    assert csv_dest_param.defaultFileExtension() == "csv"


def test_script_parsing_3():
    """
    Test script file parsing
    """
    # test display_name
    alg = RAlgorithm(description_file=script_path("test_algorithm_3.rsx"))
    alg.initAlgorithm()

    assert alg.error is None
    assert alg.name() == "thealgid"
    assert alg.displayName() == "the algo title"
    assert alg.group() == "my group"
    assert alg.groupId() == "my group"


def test_script_parsing_4():
    """
    Test script file parsing
    """
    # test that inputs are defined as parameter description
    alg = RAlgorithm(description_file=script_path("test_algorithm_4.rsx"))
    alg.initAlgorithm()

    assert alg.error is None
    assert alg.name() == "mytest"
    assert alg.displayName() == "my test"
    assert alg.group() == "my group"
    assert alg.groupId() == "my group"

    raster_param = alg.parameterDefinition("in_raster")
    assert raster_param.type() == "raster"

    vector_param = alg.parameterDefinition("in_vector")
    assert vector_param.type() == "source"

    field_param = alg.parameterDefinition("in_field")
    assert field_param.type() == "field"
    assert field_param.parentLayerParameterName() == "in_vector"

    extent_param = alg.parameterDefinition("in_extent")
    assert extent_param.type() == "extent"

    crs_param = alg.parameterDefinition("in_crs")
    assert crs_param.type() == "crs"

    string_param = alg.parameterDefinition("in_string")
    assert string_param.type() == "string"

    number_param = alg.parameterDefinition("in_number")
    assert number_param.type() == "number"
    assert number_param.dataType() == QgsProcessingParameterNumber.Integer

    enum_param = alg.parameterDefinition("in_enum")
    assert enum_param.type() == "enum"

    bool_param = alg.parameterDefinition("in_bool")
    assert bool_param.type() == "boolean"

    file_param = alg.parameterDefinition("in_file")
    assert file_param.type() == "file"
    assert file_param.behavior() == QgsProcessingParameterFile.File

    folder_param = alg.parameterDefinition("in_folder")
    assert folder_param.type() == "file"
    assert folder_param.behavior() == QgsProcessingParameterFile.Folder

    gpkg_param = alg.parameterDefinition("in_gpkg")
    assert gpkg_param.type() == "file"
    assert gpkg_param.behavior() == QgsProcessingParameterFile.File
    assert gpkg_param.extension() == "gpkg"

    img_param = alg.parameterDefinition("in_img")
    assert img_param.type() == "file"
    assert img_param.behavior() == QgsProcessingParameterFile.File
    assert img_param.extension() == ""
    assert img_param.fileFilter() == "PNG Files (*.png);; JPG Files (*.jpg *.jpeg)"

    vector_dest_param = alg.parameterDefinition("param_vector_dest")
    assert vector_dest_param.type() == "vectorDestination"
    assert vector_dest_param.dataType() == QgsProcessing.TypeVectorAnyGeometry

    vector_dest_param = alg.parameterDefinition("param_vector_point_dest")
    assert vector_dest_param.type() == "vectorDestination"
    assert vector_dest_param.dataType() == QgsProcessing.TypeVectorPoint

    vector_dest_param = alg.parameterDefinition("param_vector_line_dest")
    assert vector_dest_param.type() == "vectorDestination"
    assert vector_dest_param.dataType() == QgsProcessing.TypeVectorLine

    vector_dest_param = alg.parameterDefinition("param_vector_polygon_dest")
    assert vector_dest_param.type() == "vectorDestination"
    assert vector_dest_param.dataType() == QgsProcessing.TypeVectorPolygon

    table_dest_param = alg.parameterDefinition("param_table_dest")
    assert table_dest_param.type() == "vectorDestination"
    assert table_dest_param.dataType() == QgsProcessing.TypeVector

    raster_dest_param = alg.parameterDefinition("param_raster_dest")
    assert raster_dest_param.type() == "rasterDestination"

    folder_dest_param = alg.parameterDefinition("param_folder_dest")
    assert folder_dest_param.type() == "folderDestination"

    file_dest_param = alg.parameterDefinition("param_file_dest")
    assert file_dest_param.type() == "fileDestination"

    html_dest_param = alg.parameterDefinition("param_html_dest")
    assert html_dest_param.type() == "fileDestination"
    assert html_dest_param.fileFilter() == "HTML Files (*.html)"
    assert html_dest_param.defaultFileExtension() == "html"

    csv_dest_param = alg.parameterDefinition("param_csv_dest")
    assert csv_dest_param.type() == "fileDestination"
    assert csv_dest_param.fileFilter() == "CSV Files (*.csv)"
    assert csv_dest_param.defaultFileExtension() == "csv"

    img_dest_param = alg.parameterDefinition("param_img_dest")
    assert img_dest_param.type() == "fileDestination"
    assert img_dest_param.fileFilter() == "PNG Files (*.png);; JPG Files (*.jpg *.jpeg)"
    assert img_dest_param.defaultFileExtension() == "png"


def test_bad_syntax():
    """
    Test a bad script
    """
    alg = RAlgorithm(description_file=script_path("bad_algorithm.rsx"))
    alg.initAlgorithm()
    assert alg.name() == "bad_algorithm"
    assert alg.displayName() == "bad algorithm"
    assert alg.error == "This script has a syntax error.\nProblem with line: polyg=xvector"


def test_console_output():
    alg = RAlgorithm(description_file=script_path("test_enum_multiple.rsx"))
    alg.initAlgorithm()

    assert alg.show_console_output is True
