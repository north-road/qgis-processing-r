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
from r.processing.algorithm import RAlgorithm
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()

test_data_path = os.path.join(
    os.path.dirname(__file__),
    'data')


class AlgorithmTest(unittest.TestCase):
    """Test algorithm construction."""

    def testScriptParsing(self):
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
        self.assertEqual(alg.name(), 'test_algorithm_2')
        self.assertEqual(alg.displayName(), 'test algorithm 2')
        self.assertFalse(alg.show_plots)
        self.assertTrue(alg.use_raster_package)
        self.assertFalse(alg.pass_file_names)

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
