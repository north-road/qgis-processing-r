# coding=utf-8
"""Algorithm Test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = "(C) 2018 by Nyall Dawson"
__date__ = "20/04/2018"
__copyright__ = "Copyright 2018, North Road"
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = "$Format:%H$"

import os
import unittest

from qgis.core import (
    Qgis,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterFile,
    QgsProcessingParameterNumber,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QDate, QDateTime, QTime
from qgis.PyQt.QtGui import QColor

from processing_r.processing.algorithm import RAlgorithm

from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()

test_data_path = os.path.join(os.path.dirname(__file__), "data")


class AlgorithmTest(unittest.TestCase):
    """Test algorithm construction."""

    def testScriptParsing(self):  # pylint: disable=too-many-locals,too-many-statements
        """
        Test script file parsing
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_algorithm_1.rsx"))
        alg.initAlgorithm()
        self.assertFalse(alg.error)
        self.assertEqual(alg.name(), "test_algorithm_1")
        self.assertEqual(alg.displayName(), "test algorithm 1")
        self.assertIn("test_algorithm_1.rsx", "test_algorithm_1.rsx")
        self.assertTrue(alg.show_plots)
        self.assertTrue(alg.pass_file_names)

        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_algorithm_2.rsx"))
        alg.initAlgorithm()
        self.assertFalse(alg.error)
        self.assertEqual(alg.name(), "mytest")
        self.assertEqual(alg.displayName(), "my test")
        self.assertEqual(alg.group(), "my group")
        self.assertEqual(alg.groupId(), "my group")
        self.assertFalse(alg.show_plots)
        self.assertFalse(alg.pass_file_names)

        # test that inputs were created correctly
        raster_param = alg.parameterDefinition("in_raster")
        self.assertEqual(raster_param.type(), "raster")
        vector_param = alg.parameterDefinition("in_vector")
        self.assertEqual(vector_param.type(), "source")
        field_param = alg.parameterDefinition("in_field")
        self.assertEqual(field_param.type(), "field")
        self.assertEqual(field_param.parentLayerParameterName(), "in_vector")
        extent_param = alg.parameterDefinition("in_extent")
        self.assertEqual(extent_param.type(), "extent")
        string_param = alg.parameterDefinition("in_string")
        self.assertEqual(string_param.type(), "string")
        file_param = alg.parameterDefinition("in_file")
        self.assertEqual(file_param.type(), "file")
        number_param = alg.parameterDefinition("in_number")
        self.assertEqual(number_param.type(), "number")
        self.assertEqual(number_param.dataType(), QgsProcessingParameterNumber.Double)
        enum_param = alg.parameterDefinition("in_enum")
        self.assertEqual(enum_param.type(), "enum")
        enum_param = alg.parameterDefinition("in_enum2")
        self.assertEqual(enum_param.type(), "enum")
        self.assertEqual(enum_param.options(), ["normal", "log10", "ln", "sqrt", "exp"])
        bool_param = alg.parameterDefinition("in_bool")
        self.assertEqual(bool_param.type(), "boolean")

        # outputs
        vector_output = alg.outputDefinition("out_vector")
        self.assertEqual(vector_output.type(), "outputVector")
        self.assertEqual(vector_output.dataType(), QgsProcessing.TypeVectorAnyGeometry)
        vector_dest_param = alg.parameterDefinition("param_vector_dest")
        self.assertEqual(vector_dest_param.type(), "vectorDestination")
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorAnyGeometry)

        table_output = alg.outputDefinition("out_table")
        self.assertEqual(table_output.type(), "outputVector")
        self.assertEqual(table_output.dataType(), QgsProcessing.TypeVector)
        table_dest_param = alg.parameterDefinition("param_table_dest")
        self.assertEqual(table_dest_param.type(), "vectorDestination")
        self.assertEqual(table_dest_param.dataType(), QgsProcessing.TypeVector)

        vector_dest_param = alg.parameterDefinition("param_vector_dest2")
        self.assertEqual(vector_dest_param.type(), "vectorDestination")
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorAnyGeometry)

        vector_dest_param = alg.parameterDefinition("param_vector_point_dest")
        self.assertEqual(vector_dest_param.type(), "vectorDestination")
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorPoint)

        vector_dest_param = alg.parameterDefinition("param_vector_line_dest")
        self.assertEqual(vector_dest_param.type(), "vectorDestination")
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorLine)

        vector_dest_param = alg.parameterDefinition("param_vector_polygon_dest")
        self.assertEqual(vector_dest_param.type(), "vectorDestination")
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorPolygon)

        raster_output = alg.outputDefinition("out_raster")
        self.assertEqual(raster_output.type(), "outputRaster")
        raster_dest_param = alg.parameterDefinition("param_raster_dest")
        self.assertEqual(raster_dest_param.type(), "rasterDestination")
        number_output = alg.outputDefinition("out_number")
        self.assertEqual(number_output.type(), "outputNumber")
        string_output = alg.outputDefinition("out_string")
        self.assertEqual(string_output.type(), "outputString")
        layer_output = alg.outputDefinition("out_layer")
        self.assertEqual(layer_output.type(), "outputLayer")
        folder_output = alg.outputDefinition("out_folder")
        self.assertEqual(folder_output.type(), "outputFolder")
        folder_dest_param = alg.parameterDefinition("param_folder_dest")
        self.assertEqual(folder_dest_param.type(), "folderDestination")
        html_output = alg.outputDefinition("out_html")
        self.assertEqual(html_output.type(), "outputHtml")
        html_dest_param = alg.parameterDefinition("param_html_dest")
        self.assertEqual(html_dest_param.type(), "fileDestination")
        file_output = alg.outputDefinition("out_file")
        self.assertEqual(file_output.type(), "outputFile")
        file_dest_param = alg.parameterDefinition("param_file_dest")
        self.assertEqual(file_dest_param.type(), "fileDestination")
        csv_output = alg.outputDefinition("out_csv")
        self.assertEqual(csv_output.type(), "outputFile")
        csv_dest_param = alg.parameterDefinition("param_csv_dest")
        self.assertEqual(csv_dest_param.type(), "fileDestination")
        self.assertEqual(csv_dest_param.defaultFileExtension(), "csv")

        # test display_name
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_algorithm_3.rsx"))
        alg.initAlgorithm()
        self.assertFalse(alg.error)
        self.assertEqual(alg.name(), "thealgid")
        self.assertEqual(alg.displayName(), "the algo title")
        self.assertEqual(alg.group(), "my group")
        self.assertEqual(alg.groupId(), "my group")

        # test that inputs are defined as parameter description
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_algorithm_4.rsx"))
        alg.initAlgorithm()
        self.assertFalse(alg.error)
        self.assertEqual(alg.name(), "mytest")
        self.assertEqual(alg.displayName(), "my test")
        self.assertEqual(alg.group(), "my group")
        self.assertEqual(alg.groupId(), "my group")

        raster_param = alg.parameterDefinition("in_raster")
        self.assertEqual(raster_param.type(), "raster")
        vector_param = alg.parameterDefinition("in_vector")
        self.assertEqual(vector_param.type(), "source")
        field_param = alg.parameterDefinition("in_field")
        self.assertEqual(field_param.type(), "field")
        self.assertEqual(field_param.parentLayerParameterName(), "in_vector")
        extent_param = alg.parameterDefinition("in_extent")
        self.assertEqual(extent_param.type(), "extent")
        crs_param = alg.parameterDefinition("in_crs")
        self.assertEqual(crs_param.type(), "crs")
        string_param = alg.parameterDefinition("in_string")
        self.assertEqual(string_param.type(), "string")
        number_param = alg.parameterDefinition("in_number")
        self.assertEqual(number_param.type(), "number")
        self.assertEqual(number_param.dataType(), QgsProcessingParameterNumber.Integer)
        enum_param = alg.parameterDefinition("in_enum")
        self.assertEqual(enum_param.type(), "enum")
        bool_param = alg.parameterDefinition("in_bool")
        self.assertEqual(bool_param.type(), "boolean")

        file_param = alg.parameterDefinition("in_file")
        self.assertEqual(file_param.type(), "file")
        self.assertEqual(file_param.behavior(), QgsProcessingParameterFile.File)
        folder_param = alg.parameterDefinition("in_folder")
        self.assertEqual(folder_param.type(), "file")
        self.assertEqual(folder_param.behavior(), QgsProcessingParameterFile.Folder)
        gpkg_param = alg.parameterDefinition("in_gpkg")
        self.assertEqual(gpkg_param.type(), "file")
        self.assertEqual(gpkg_param.behavior(), QgsProcessingParameterFile.File)
        self.assertEqual(gpkg_param.extension(), "gpkg")
        img_param = alg.parameterDefinition("in_img")
        self.assertEqual(img_param.type(), "file")
        self.assertEqual(img_param.behavior(), QgsProcessingParameterFile.File)
        self.assertEqual(img_param.extension(), "")
        self.assertEqual(img_param.fileFilter(), "PNG Files (*.png);; JPG Files (*.jpg *.jpeg)")

        vector_dest_param = alg.parameterDefinition("param_vector_dest")
        self.assertEqual(vector_dest_param.type(), "vectorDestination")
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorAnyGeometry)
        vector_dest_param = alg.parameterDefinition("param_vector_point_dest")
        self.assertEqual(vector_dest_param.type(), "vectorDestination")
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorPoint)
        vector_dest_param = alg.parameterDefinition("param_vector_line_dest")
        self.assertEqual(vector_dest_param.type(), "vectorDestination")
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorLine)
        vector_dest_param = alg.parameterDefinition("param_vector_polygon_dest")
        self.assertEqual(vector_dest_param.type(), "vectorDestination")
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorPolygon)
        table_dest_param = alg.parameterDefinition("param_table_dest")
        self.assertEqual(table_dest_param.type(), "vectorDestination")
        self.assertEqual(table_dest_param.dataType(), QgsProcessing.TypeVector)
        raster_dest_param = alg.parameterDefinition("param_raster_dest")
        self.assertEqual(raster_dest_param.type(), "rasterDestination")

        folder_dest_param = alg.parameterDefinition("param_folder_dest")
        self.assertEqual(folder_dest_param.type(), "folderDestination")
        file_dest_param = alg.parameterDefinition("param_file_dest")
        self.assertEqual(file_dest_param.type(), "fileDestination")
        html_dest_param = alg.parameterDefinition("param_html_dest")
        self.assertEqual(html_dest_param.type(), "fileDestination")
        self.assertEqual(html_dest_param.fileFilter(), "HTML Files (*.html)")
        self.assertEqual(html_dest_param.defaultFileExtension(), "html")
        csv_dest_param = alg.parameterDefinition("param_csv_dest")
        self.assertEqual(csv_dest_param.type(), "fileDestination")
        self.assertEqual(csv_dest_param.fileFilter(), "CSV Files (*.csv)")
        self.assertEqual(csv_dest_param.defaultFileExtension(), "csv")
        img_dest_param = alg.parameterDefinition("param_img_dest")
        self.assertEqual(img_dest_param.type(), "fileDestination")
        self.assertEqual(img_dest_param.fileFilter(), "PNG Files (*.png);; JPG Files (*.jpg *.jpeg)")
        self.assertEqual(img_dest_param.defaultFileExtension(), "png")

    def testBadAlgorithm(self):
        """
        Test a bad script
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "bad_algorithm.rsx"))
        alg.initAlgorithm()
        self.assertEqual(alg.name(), "bad_algorithm")
        self.assertEqual(alg.displayName(), "bad algorithm")
        self.assertEqual(alg.error, "This script has a syntax error.\nProblem with line: polyg=xvector")

    def testInputs(self):
        """
        Test creation of script with algorithm inputs
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_algorithm_2.rsx"))
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        # enum evaluation
        script = alg.build_import_commands({"in_enum": 0}, context, feedback)
        self.assertIn("in_enum <- 0", script)

        # boolean evaluation
        script = alg.build_import_commands({"in_bool": True}, context, feedback)
        self.assertIn("in_bool <- TRUE", script)
        script = alg.build_import_commands({"in_bool": False}, context, feedback)
        self.assertIn("in_bool <- FALSE", script)

        # number evaluation
        script = alg.build_import_commands({"in_number": None}, context, feedback)
        self.assertIn("in_number <- NULL", script)
        script = alg.build_import_commands({"in_number": 5}, context, feedback)
        self.assertIn("in_number <- 5.0", script)
        script = alg.build_import_commands({"in_number": 5.5}, context, feedback)
        self.assertIn("in_number <- 5.5", script)

        # folder destination
        script = alg.build_import_commands(
            {"param_folder_dest": "/tmp/processing/test_algorithm_2_r/"}, context, feedback
        )

        # file destination
        script = alg.build_import_commands(
            {"param_html_dest": "/tmp/processing/test_algorithm_2_r/dest.html"}, context, feedback
        )
        self.assertIn('param_html_dest <- "/tmp/processing/test_algorithm_2_r/dest.html"', script)
        script = alg.build_import_commands(
            {"param_file_dest": "/tmp/processing/test_algorithm_2_r/dest.file"}, context, feedback
        )
        self.assertIn('param_file_dest <- "/tmp/processing/test_algorithm_2_r/dest.file"', script)
        script = alg.build_import_commands(
            {"param_csv_dest": "/tmp/processing/test_algorithm_2_r/dest.csv"}, context, feedback
        )
        self.assertIn('param_csv_dest <- "/tmp/processing/test_algorithm_2_r/dest.csv"', script)

    def testReadSf(self):
        """
        Test reading vector inputs
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_vectorin.rsx"))
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        script = alg.build_import_commands({"Layer": os.path.join(test_data_path, "lines.shp")}, context, feedback)

        USE_NEW_API = Qgis.QGIS_VERSION_INT >= 30900 and hasattr(
            QgsProcessingAlgorithm, "parameterAsCompatibleSourceLayerPathAndLayerName"
        )
        if USE_NEW_API:
            self.assertEqual(
                script[0],
                'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(
                    os.path.join(test_data_path, "lines.shp")
                ),
            )
        else:
            self.assertEqual(
                script[0],
                'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(
                    os.path.join(test_data_path, "lines.shp")
                ),
            )
        script = alg.build_import_commands(
            {"Layer": os.path.join(test_data_path, "lines.shp").replace("/", "\\")}, context, feedback
        )
        if USE_NEW_API:
            self.assertEqual(
                script[0],
                'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(
                    os.path.join(test_data_path, "lines.shp")
                ),
            )
        else:
            self.assertEqual(
                script[0],
                'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(
                    os.path.join(test_data_path, "lines.shp")
                ),
            )
        vl = QgsVectorLayer(os.path.join(test_data_path, "test_gpkg.gpkg") + "|layername=points")
        self.assertTrue(vl.isValid())
        vl2 = QgsVectorLayer(os.path.join(test_data_path, "test_gpkg.gpkg") + "|layername=lines")
        self.assertTrue(vl2.isValid())
        script = alg.build_import_commands({"Layer": vl, "Layer2": vl2}, context, feedback)

        if USE_NEW_API:
            # use the newer api and avoid unnecessary layer translation
            self.assertEqual(
                script,
                [
                    'Layer <- st_read("{}", layer = "points", quiet = TRUE, stringsAsFactors = FALSE)'.format(
                        os.path.join(test_data_path, "test_gpkg.gpkg")
                    ),
                    'Layer2 <- st_read("{}", layer = "lines", quiet = TRUE, stringsAsFactors = FALSE)'.format(
                        os.path.join(test_data_path, "test_gpkg.gpkg")
                    ),
                ],
            )
        else:
            # older version, forced to use inefficient api
            self.assertIn('Layer <- st_read("/tmp', script[0])
            self.assertIn('Layer2 <- st_read("/tmp', script[1])

    def testRasterIn(self):
        """
        Test reading raster inputs
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_rasterin.rsx"))
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        script = alg.build_import_commands({"Layer": os.path.join(test_data_path, "dem.tif")}, context, feedback)
        self.assertEqual(script, ['Layer <- brick("{}")'.format(os.path.join(test_data_path, "dem.tif"))])
        script = alg.build_import_commands(
            {"Layer": os.path.join(test_data_path, "dem.tif").replace("/", "\\")}, context, feedback
        )
        self.assertEqual(script, ['Layer <- brick("{}")'.format(os.path.join(test_data_path, "dem.tif"))])
        script = alg.build_import_commands({"Layer": None}, context, feedback)
        self.assertEqual(script, ["Layer <- NULL"])

        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_rasterin_names.rsx"))
        alg.initAlgorithm()
        script = alg.build_import_commands({"Layer": os.path.join(test_data_path, "dem.tif")}, context, feedback)
        self.assertEqual(script, ['Layer <- "{}"'.format(os.path.join(test_data_path, "dem.tif"))])
        script = alg.build_import_commands({"Layer": None}, context, feedback)
        self.assertEqual(script, ["Layer <- NULL"])

    def testMultiRasterIn(self):
        """
        Test raster multilayer input parameter
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_multirasterin.rsx"))
        alg.initAlgorithm()
        raster_param = alg.parameterDefinition("Layer")
        self.assertEqual(raster_param.type(), "multilayer")
        self.assertEqual(raster_param.layerType(), QgsProcessing.TypeRaster)

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        script = alg.build_import_commands(
            {"Layer": [os.path.join(test_data_path, "dem.tif"), os.path.join(test_data_path, "dem2.tif")]},
            context,
            feedback,
        )
        self.assertEqual(
            script,
            [
                'tempvar0 <- brick("{}")'.format(os.path.join(test_data_path, "dem.tif")),
                'tempvar1 <- brick("{}")'.format(os.path.join(test_data_path, "dem2.tif")),
                "Layer = list(tempvar0,tempvar1)",
            ],
        )
        script = alg.build_import_commands({"Layer": []}, context, feedback)
        self.assertEqual(script, ["Layer = list()"])

    def testMultiVectorIn(self):
        """
        Test vector multilayer input parameter
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_multivectorin.rsx"))
        alg.initAlgorithm()
        param = alg.parameterDefinition("Layer")
        self.assertEqual(param.type(), "multilayer")
        self.assertEqual(param.layerType(), QgsProcessing.TypeVectorAnyGeometry)

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        script = alg.build_import_commands(
            {"Layer": [os.path.join(test_data_path, "lines.shp"), os.path.join(test_data_path, "points.gml")]},
            context,
            feedback,
        )
        self.assertEqual(
            script,
            [
                'tempvar0 <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(
                    os.path.join(test_data_path, "lines.shp")
                ),
                'tempvar1 <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(
                    os.path.join(test_data_path, "points.gml")
                ),
                "Layer = list(tempvar0,tempvar1)",
            ],
        )
        script = alg.build_import_commands({"Layer": []}, context, feedback)
        self.assertEqual(script, ["Layer = list()"])

    def testMultiFieldIn(self):
        """
        Test multiple field input parameter
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_field_multiple.rsx"))
        alg.initAlgorithm()
        param = alg.parameterDefinition("MultiField")
        self.assertEqual(param.type(), "field")
        self.assertTrue(param.allowMultiple())

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        script = alg.build_import_commands({"Layer": os.path.join(test_data_path, "lines.shp")}, context, feedback)
        self.assertEqual(
            script,
            [
                'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(
                    os.path.join(test_data_path, "lines.shp")
                ),
                "MultiField <- NULL",
            ],
        )
        script = alg.build_import_commands(
            {"Layer": os.path.join(test_data_path, "lines.shp"), "MultiField": ["a"]}, context, feedback
        )
        self.assertEqual(
            script,
            [
                'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(
                    os.path.join(test_data_path, "lines.shp")
                ),
                'MultiField <- c("a")',
            ],
        )
        script = alg.build_import_commands(
            {"Layer": os.path.join(test_data_path, "lines.shp"), "MultiField": ["a", 'b"c']}, context, feedback
        )
        self.assertEqual(
            script,
            [
                'Layer <- st_read("{}", quiet = TRUE, stringsAsFactors = FALSE)'.format(
                    os.path.join(test_data_path, "lines.shp")
                ),
                'MultiField <- c("a","b\\"c")',
            ],
        )

    def testVectorOutputs(self):
        """
        Test writing vector outputs
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_vectorout.rsx"))
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        script = alg.build_export_commands(
            {"Output": "/home/test/lines.shp", "OutputCSV": "/home/test/tab.csv"}, context, feedback
        )
        self.assertEqual(
            script,
            [
                'st_write(Output, "/home/test/lines.shp", layer = "lines", quiet = TRUE)',
                'write.csv(OutputCSV, "/home/test/tab.csv", row.names = FALSE)',
            ],
        )
        script = alg.build_export_commands(
            {"Output": "/home/test/lines.gpkg", "OutputCSV": "/home/test/tab.csv"}, context, feedback
        )
        self.assertEqual(
            script,
            [
                'st_write(Output, "/home/test/lines.gpkg", layer = "lines", quiet = TRUE)',
                'write.csv(OutputCSV, "/home/test/tab.csv", row.names = FALSE)',
            ],
        )

    def testMultiOutputs(self):
        """
        Test writing vector outputs
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_multiout.rsx"))
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        script = alg.build_export_commands(
            {"Output": "/home/test/lines.shp", "OutputCSV": "/home/test/tab.csv", "OutputFile": "/home/test/file.csv"},
            context,
            feedback,
        )

        self.assertIn('st_write(Output, "/home/test/lines.shp", layer = "lines", quiet = TRUE)', script)
        self.assertIn('write.csv(OutputCSV, "/home/test/tab.csv", row.names = FALSE)', script)
        self.assertTrue(script[2].startswith('cat("##OutputFile", file='), script[2])
        self.assertTrue(script[3].startswith("cat(OutputFile, file="), script[3])
        self.assertTrue(script[4].startswith('cat("##OutputNum", file='), script[4])
        self.assertTrue(script[5].startswith("cat(OutputNum, file="), script[5])
        self.assertTrue(script[6].startswith('cat("##OutputStr", file='), script[6])
        self.assertTrue(script[7].startswith("cat(OutputStr, file="), script[7])

    def testEnums(self):
        """
        Test for both enum types
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_enums.rsx"))
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        script = alg.build_import_commands({"enum_normal": 0}, context, feedback)
        self.assertIn("enum_normal <- 0", script)
        script = alg.build_import_commands({"enum_string": 0}, context, feedback)
        self.assertIn('enum_string <- "enum_a"', script)

    def testEnumsMultiple(self):
        """
        Test for both enum multiple types
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_enum_multiple.rsx"))
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        params = {"enum_normal": [0, 1], "enum_string": [0, 1], "R_CONSOLE_OUTPUT": "TEMPORARY_OUTPUT"}

        script = alg.build_import_commands(params, context, feedback)

        self.assertIn("enum_normal <- c(0, 1)", script)
        self.assertIn('enum_string <- c("enum_a","enum_b")', script)
        self.assertIn("enum_string_optional <- NULL", script)
        self.assertIn("enum_normal_optional <- NULL", script)

        params = {
            "enum_normal": [0, 1, 2],
            "enum_string": [0, 2],
            "enum_string_optional": [0],
            "enum_normal_optional": [1],
            "R_CONSOLE_OUTPUT": "TEMPORARY_OUTPUT",
        }

        script = alg.build_import_commands(params, context, feedback)

        self.assertIn("enum_normal <- c(0, 1, 2)", script)
        self.assertIn('enum_string <- c("enum_a","enum_c")', script)
        self.assertIn('enum_string_optional <- c("enum_a")', script)
        self.assertIn("enum_normal_optional <- c(1)", script)

    def testAlgHelp(self):  # pylint: disable=too-many-locals,too-many-statements
        """
        Test algorithm help
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_algorithm_1.rsx"))
        alg.initAlgorithm()
        self.assertIn("A polygon layer", alg.shortHelpString())
        self.assertIn("Me2", alg.shortHelpString())
        self.assertIn("Test help.", alg.shortHelpString())

        # param help
        if Qgis.QGIS_VERSION_INT >= 31604:
            polyg_param = alg.parameterDefinition("polyg")
            self.assertEqual(polyg_param.help(), "A polygon layer")

        # no help file
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_algorithm_2.rsx"))
        alg.initAlgorithm()
        self.assertEqual(alg.shortHelpString(), "")

        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_algorithm_inline_help.rsx"))
        alg.initAlgorithm()
        self.assertIn("A polygon layer", alg.shortHelpString())
        self.assertIn("Me2", alg.shortHelpString())
        self.assertIn("Test help.", alg.shortHelpString())

        # param help
        if Qgis.QGIS_VERSION_INT >= 31604:
            polyg_param = alg.parameterDefinition("polyg")
            self.assertEqual(polyg_param.help(), "A polygon layer description from multi-lines")

    def testAlgDontLoadAnyPackages(self):
        """
        Test dont_load_any_packages keyword
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_dont_load_any_packages.rsx"))
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        script = alg.build_r_script({}, context, feedback)
        self.assertNotIn('library("sf")', script)
        self.assertNotIn('library("raster")', script)
        self.assertNotIn('library("rgdal")', script)
        self.assertNotIn('library("sp")', script)

    def testAlgPointInput(self):
        """
        Test Point parameter
        """

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_input_point.rsx"))
        alg.initAlgorithm()

        script = alg.build_r_script({"point": "20.219926,49.138354 [EPSG:4326]"}, context, feedback)

        self.assertIn('library("sf")', script)
        self.assertIn("point <- st_sfc(st_point(c(20.219926,49.138354)), crs = point_crs)", script)

    def testAlgRangeInput(self):
        """
        Test range parameter
        """

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_input_range.rsx"))
        alg.initAlgorithm()

        script = alg.build_r_script({"range": [0, 1]}, context, feedback)
        self.assertIn("range <- c(min = 0.0, max = 1.0)", script)
        script = alg.build_r_script({"range": [5, 10]}, context, feedback)
        self.assertIn("range <- c(min = 5.0, max = 10.0)", script)
        script = alg.build_r_script({"range": [0.5, 1.5]}, context, feedback)
        self.assertIn("range <- c(min = 0.5, max = 1.5)", script)

    def testAlgColorInput(self):
        """
        Test color parameter
        """

        if Qgis.QGIS_VERSION_INT < 31000:
            self.skipTest("QGIS version does not support this.")

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_input_color.rsx"))
        alg.initAlgorithm()

        script = alg.build_r_script({"color": QColor(0, 255, 0)}, context, feedback)
        self.assertIn("color <- rgb(0, 255, 0, 255, maxColorValue = 255)", script)
        script = alg.build_r_script({"color": QColor(255, 0, 0)}, context, feedback)
        self.assertIn("color <- rgb(255, 0, 0, 255, maxColorValue = 255)", script)

    def testAlgDateTimeInput(self):
        """
        Test datetime parameter
        """

        if Qgis.QGIS_VERSION_INT < 31400:
            self.skipTest("QGIS version does not support this.")

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_input_datetime.rsx"))
        alg.initAlgorithm()

        script = alg.build_r_script({"datetime": QDateTime(QDate(2021, 10, 1), QTime(16, 57, 0))}, context, feedback)
        self.assertIn('datetime <- as.POSIXct("2021-10-01T16:57:00", format = "%Y-%m-%dT%H:%M:%S")', script)
        script = alg.build_r_script({"datetime": QDateTime(QDate(2021, 10, 14), QTime(14, 48, 52))}, context, feedback)
        self.assertIn('datetime <- as.POSIXct("2021-10-14T14:48:52", format = "%Y-%m-%dT%H:%M:%S")', script)

    def testAlgExpressions(self):
        """
        Test Expression parameter
        """

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_input_expression.rsx"))
        alg.initAlgorithm()

        script = alg.build_r_script({""}, context, feedback)

        self.assertIn("number <- 6", script)
        self.assertTrue(
            any(['geometry <- sf::st_as_sfc("Polygon ' in line for line in script])
        )  # pylint: disable=use-a-generator
        self.assertIn('date_a <- as.POSIXct("2020-05-04", format = "%Y-%m-%d")', script)
        self.assertIn('time_a <- lubridate::hms("13:45:30")', script)

    def testAlgRasterBand(self):
        """
        Test datetime parameter
        """

        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_raster_band.rsx"))
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        script = alg.build_import_commands(
            {"Band": 1, "Layer": os.path.join(test_data_path, "dem.tif")}, context, feedback
        )
        self.assertIn("Band <- 1", script)

    def testAlgLibraryWithOptions(self):
        """
        Test library with options
        """

        alg = RAlgorithm(description_file=os.path.join(test_data_path, "test_library_with_option.rsx"))
        alg.initAlgorithm()

        script = alg.r_templates.build_script_header_commands(alg.script)

        self.assertIn(
            'tryCatch(find.package("MASS"), error = function(e) install.packages("MASS", dependencies=TRUE))', script
        )
        self.assertIn(
            'tryCatch(find.package("Matrix"), error = function(e) install.packages("Matrix", dependencies=TRUE))',
            script,
        )
        self.assertIn('library("MASS", quietly=True)', script)
        self.assertIn('library("Matrix")', script)


if __name__ == "__main__":
    suite = unittest.makeSuite(AlgorithmTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
