# coding=utf-8
"""Algorithm Test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = '(C) 2018 by Nyall Dawson'
__date__ = '20/04/2018'
__copyright__ = 'Copyright 2018, North Road'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import unittest
import os
from qgis.core import (QgsProcessingParameterNumber,
                       QgsProcessing,
                       QgsProcessingContext,
                       QgsProcessingFeedback,
                       QgsVectorLayer)
from r.processing.algorithm import RAlgorithm
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()

test_data_path = os.path.join(
    os.path.dirname(__file__),
    'data')


class AlgorithmTest(unittest.TestCase):
    """Test algorithm construction."""

    def testScriptParsing(self):  # pylint: disable=too-many-locals,too-many-statements
        """
        Test script file parsing
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, 'test_algorithm_1.rsx'))
        alg.initAlgorithm()
        self.assertFalse(alg.error)
        self.assertEqual(alg.name(), 'test_algorithm_1')
        self.assertEqual(alg.displayName(), 'test algorithm 1')
        self.assertEqual(alg.shortDescription(), os.path.join(test_data_path, 'test_algorithm_1.rsx'))
        self.assertTrue(alg.show_plots)
        self.assertFalse(alg.use_raster_package)
        self.assertTrue(alg.pass_file_names)

        alg = RAlgorithm(description_file=os.path.join(test_data_path, 'test_algorithm_2.rsx'))
        alg.initAlgorithm()
        self.assertFalse(alg.error)
        self.assertEqual(alg.name(), 'mytest')
        self.assertEqual(alg.displayName(), 'my test')
        self.assertEqual(alg.group(), 'my group')
        self.assertEqual(alg.groupId(), 'my group')
        self.assertFalse(alg.show_plots)
        self.assertTrue(alg.use_raster_package)
        self.assertFalse(alg.pass_file_names)

        # test that inputs were created correctly
        raster_param = alg.parameterDefinition('in_raster')
        self.assertEqual(raster_param.type(), 'raster')
        vector_param = alg.parameterDefinition('in_vector')
        self.assertEqual(vector_param.type(), 'vector')
        field_param = alg.parameterDefinition('in_field')
        self.assertEqual(field_param.type(), 'field')
        self.assertEqual(field_param.parentLayerParameterName(), 'in_vector')
        extent_param = alg.parameterDefinition('in_extent')
        self.assertEqual(extent_param.type(), 'extent')
        string_param = alg.parameterDefinition('in_string')
        self.assertEqual(string_param.type(), 'string')
        file_param = alg.parameterDefinition('in_file')
        self.assertEqual(file_param.type(), 'file')
        number_param = alg.parameterDefinition('in_number')
        self.assertEqual(number_param.type(), 'number')
        self.assertEqual(number_param.dataType(), QgsProcessingParameterNumber.Double)
        enum_param = alg.parameterDefinition('in_enum')
        self.assertEqual(enum_param.type(), 'enum')
        enum_param = alg.parameterDefinition('in_enum2')
        self.assertEqual(enum_param.type(), 'enum')
        self.assertEqual(enum_param.options(), ['normal', 'log10', 'ln', 'sqrt', 'exp'])
        bool_param = alg.parameterDefinition('in_bool')
        self.assertEqual(bool_param.type(), 'boolean')

        # outputs
        vector_output = alg.outputDefinition('out_vector')
        self.assertEqual(vector_output.type(), 'outputVector')
        vector_dest_param = alg.parameterDefinition('param_vector_dest')
        self.assertEqual(vector_dest_param.type(), 'vectorDestination')
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorAnyGeometry)

        vector_dest_param = alg.parameterDefinition('param_vector_dest2')
        self.assertEqual(vector_dest_param.type(), 'vectorDestination')
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorAnyGeometry)

        vector_dest_param = alg.parameterDefinition('param_vector_point_dest')
        self.assertEqual(vector_dest_param.type(), 'vectorDestination')
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorPoint)

        vector_dest_param = alg.parameterDefinition('param_vector_line_dest')
        self.assertEqual(vector_dest_param.type(), 'vectorDestination')
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorLine)

        vector_dest_param = alg.parameterDefinition('param_vector_polygon_dest')
        self.assertEqual(vector_dest_param.type(), 'vectorDestination')
        self.assertEqual(vector_dest_param.dataType(), QgsProcessing.TypeVectorPolygon)

        raster_output = alg.outputDefinition('out_raster')
        self.assertEqual(raster_output.type(), 'outputRaster')
        raster_dest_param = alg.parameterDefinition('param_raster_dest')
        self.assertEqual(raster_dest_param.type(), 'rasterDestination')
        number_output = alg.outputDefinition('out_number')
        self.assertEqual(number_output.type(), 'outputNumber')
        string_output = alg.outputDefinition('out_string')
        self.assertEqual(string_output.type(), 'outputString')
        layer_output = alg.outputDefinition('out_layer')
        self.assertEqual(layer_output.type(), 'outputLayer')
        folder_output = alg.outputDefinition('out_folder')
        self.assertEqual(folder_output.type(), 'outputFolder')
        folder_dest_param = alg.parameterDefinition('param_folder_dest')
        self.assertEqual(folder_dest_param.type(), 'folderDestination')
        html_output = alg.outputDefinition('out_html')
        self.assertEqual(html_output.type(), 'outputHtml')
        html_dest_param = alg.parameterDefinition('param_html_dest')
        self.assertEqual(html_dest_param.type(), 'fileDestination')

    def testBadAlgorithm(self):
        """
        Test a bad script
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, 'bad_algorithm.rsx'))
        alg.initAlgorithm()
        self.assertEqual(alg.name(), 'bad_algorithm')
        self.assertEqual(alg.displayName(), 'bad algorithm')
        self.assertEqual(alg.error, 'This script has a syntax error.\nProblem with line: polyg=xvector')

    def testInputs(self):
        """
        Test creation of script with algorithm inputs
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, 'test_algorithm_2.rsx'))
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        # enum evaluation
        script = alg.build_import_commands({'in_enum': 0}, context, feedback)
        self.assertIn('in_enum=0', script)

        # boolean evaluation
        script = alg.build_import_commands({'in_bool': True}, context, feedback)
        self.assertIn('in_bool=TRUE', script)
        script = alg.build_import_commands({'in_bool': False}, context, feedback)
        self.assertIn('in_bool=FALSE', script)

    def testReadOgr(self):
        """
        Test reading vector inputs
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, 'test_vectorin.rsx'))
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        script = alg.build_import_commands({'Layer': os.path.join(test_data_path, 'lines.shp')}, context, feedback)
        self.assertEqual(script, ['Layer=readOGR("{}",layer="lines")'.format(test_data_path)])
        vl = QgsVectorLayer(os.path.join(test_data_path, 'test_gpkg.gpkg') + '|layername=points')
        self.assertTrue(vl.isValid())
        script = alg.build_import_commands({'Layer': vl}, context, feedback)
        self.assertEqual(script,
                         ['Layer=readOGR("{}",layer="points")'.format(os.path.join(test_data_path, 'test_gpkg.gpkg'))])
        vl = QgsVectorLayer(os.path.join(test_data_path, 'test_gpkg.gpkg') + '|layername=lines')
        self.assertTrue(vl.isValid())
        script = alg.build_import_commands({'Layer': vl}, context, feedback)
        self.assertEqual(script,
                         ['Layer=readOGR("{}",layer="lines")'.format(os.path.join(test_data_path, 'test_gpkg.gpkg'))])

    def testVectorOutputs(self):
        """
        Test writing vector outputs
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, 'test_vectorout.rsx'))
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        script = alg.build_export_commands({'Output': '/home/test/lines.shp'}, context, feedback)
        self.assertEqual(script, ['writeOGR(Output,"/home/test/lines.shp","lines", driver="ESRI Shapefile")'])
        script = alg.build_export_commands({'Output': '/home/test/lines.gpkg'}, context, feedback)
        self.assertEqual(script, ['writeOGR(Output,"/home/test/lines.gpkg","lines", driver="GPKG")'])

    def testAlgHelp(self):  # pylint: disable=too-many-locals,too-many-statements
        """
        Test algorithm help
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, 'test_algorithm_1.rsx'))
        alg.initAlgorithm()
        self.assertIn('A polygon layer', alg.shortHelpString())
        self.assertIn('Me2', alg.shortHelpString())
        self.assertIn('Test help.', alg.shortHelpString())

        # no help file
        alg = RAlgorithm(description_file=os.path.join(test_data_path, 'test_algorithm_2.rsx'))
        alg.initAlgorithm()
        self.assertFalse(alg.shortHelpString())


if __name__ == "__main__":
    suite = unittest.makeSuite(AlgorithmTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
