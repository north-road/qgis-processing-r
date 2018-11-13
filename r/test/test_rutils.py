# coding=utf-8
"""R Utils Test.

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

import os
import unittest
from r.processing.utils import RUtils
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class RUtilsTest(unittest.TestCase):
    """Test RUtils work."""

    def testBuiltInPath(self):
        """
        Tests built in scripts path
        """
        self.assertTrue(RUtils.builtin_scripts_folder())
        self.assertIn('builtin_scripts', RUtils.builtin_scripts_folder())
        self.assertTrue(os.path.exists(RUtils.builtin_scripts_folder()))

    def testDefaultScriptsFolder(self):
        """
        Tests default user scripts folder
        """
        self.assertTrue(RUtils.default_scripts_folder())
        self.assertIn('rscripts', RUtils.default_scripts_folder())
        self.assertTrue(os.path.exists(RUtils.default_scripts_folder()))

    def testScriptsFolders(self):
        """
        Test script folders
        """
        self.assertTrue(RUtils.script_folders())
        self.assertIn(RUtils.default_scripts_folder(), RUtils.script_folders())
        self.assertIn(RUtils.builtin_scripts_folder(), RUtils.script_folders())


if __name__ == "__main__":
    suite = unittest.makeSuite(RUtilsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
