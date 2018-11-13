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
from qgis.core import QgsProcessingParameterNumber
from r.processing.algorithm import RAlgorithm
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()

test_data_path = os.path.join(
    os.path.dirname(__file__),
    'data')


class AlgorithmTest(unittest.TestCase):
    """Test algorithm construction."""

    def testScriptParsing(self):  # pylint: disable=too-many-locals
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
        bool_param = alg.parameterDefinition('in_bool')
        self.assertEqual(bool_param.type(), 'boolean')

        # outputs
        vector_output = alg.outputDefinition('out_vector')
        self.assertEqual(vector_output.type(), 'outputVector')
        raster_output = alg.outputDefinition('out_raster')
        self.assertEqual(raster_output.type(), 'outputRaster')
        number_output = alg.outputDefinition('out_number')
        self.assertEqual(number_output.type(), 'outputNumber')
        string_output = alg.outputDefinition('out_string')
        self.assertEqual(string_output.type(), 'outputString')

    def testBadAlgorithm(self):
        """
        Test a bad script
        """
        alg = RAlgorithm(description_file=os.path.join(test_data_path, 'bad_algorithm.rsx'))
        alg.initAlgorithm()
        self.assertEqual(alg.name(), 'bad_algorithm')
        self.assertEqual(alg.displayName(), 'bad algorithm')
        self.assertEqual(alg.error, 'This script has a syntax error.\nProblem with line: polyg=xvector')


if __name__ == "__main__":
    suite = unittest.makeSuite(AlgorithmTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
