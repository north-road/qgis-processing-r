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
from qgis.PyQt.QtCore import QCoreApplication, QSettings
from processing.core.ProcessingConfig import ProcessingConfig
from processing_r.processing.utils import RUtils
from processing_r.processing.provider import RAlgorithmProvider
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class RUtilsTest(unittest.TestCase):
    """Test RUtils work."""

    def __init__(self, methodName):
        """Run before all tests and set up environment"""
        super().__init__(methodName)

        # Don't mess with actual user settings
        QCoreApplication.setOrganizationName("North Road")
        QCoreApplication.setOrganizationDomain("qgis.org")
        QCoreApplication.setApplicationName("QGIS-R")
        QSettings().clear()

        # make Provider settings available
        self.provider = RAlgorithmProvider()
        self.provider.load()

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

    def testDescriptiveName(self):
        """
        Tests creating descriptive name
        """
        self.assertEqual(RUtils.create_descriptive_name('a B_4324_asd'), 'a B 4324 asd')

    def testStripSpecialCharacters(self):
        """
        Tests stripping special characters from a name
        """
        self.assertEqual(RUtils.strip_special_characters('aB 43 24a:sd'), 'aB4324asd')

    def test_is_windows(self):
        """
        Test is_windows
        """
        self.assertFalse(RUtils.is_windows())  # suck it, Windows users!

    def test_is_macos(self):
        """
        Test is_macos
        """
        self.assertFalse(RUtils.is_macos())  # suck it even more, MacOS users!

    def test_guess_r_binary_folder(self):
        """
        Test guessing the R binary folder -- not much to do here, all the logic is Windows specific
        """
        self.assertFalse(RUtils.guess_r_binary_folder())

    def test_r_binary_folder(self):
        """
        Test retrieving R binary folder
        """
        self.assertFalse(RUtils.r_binary_folder())
        ProcessingConfig.setSettingValue(RUtils.R_FOLDER, '/usr/local/bin')
        self.assertEqual(RUtils.r_binary_folder(), '/usr/local/bin')
        ProcessingConfig.setSettingValue(RUtils.R_FOLDER, None)
        self.assertFalse(RUtils.r_binary_folder())

    def test_r_executable(self):
        """
        Test retrieving R executable
        """
        self.assertEqual(RUtils.path_to_r_executable(), 'R')
        self.assertEqual(RUtils.path_to_r_executable(script_executable=True), 'Rscript')
        ProcessingConfig.setSettingValue(RUtils.R_FOLDER, '/usr/local/bin')
        self.assertEqual(RUtils.path_to_r_executable(), '/usr/local/bin/R')
        self.assertEqual(RUtils.path_to_r_executable(script_executable=True), '/usr/local/bin/Rscript')
        ProcessingConfig.setSettingValue(RUtils.R_FOLDER, None)
        self.assertEqual(RUtils.path_to_r_executable(), 'R')
        self.assertEqual(RUtils.path_to_r_executable(script_executable=True), 'Rscript')

    def test_package_repo(self):
        """
        Test retrieving/setting the package repo
        """
        self.assertEqual(RUtils.package_repo(), 'http://cran.at.r-project.org/')
        ProcessingConfig.setSettingValue(RUtils.R_REPO, 'http://mirror.at.r-project.org/')
        self.assertEqual(RUtils.package_repo(), 'http://mirror.at.r-project.org/')
        ProcessingConfig.setSettingValue(RUtils.R_REPO, 'http://cran.at.r-project.org/')
        self.assertEqual(RUtils.package_repo(), 'http://cran.at.r-project.org/')

    def test_use_user_library(self):
        """
        Test retrieving/setting the user library setting
        """
        self.assertTrue(RUtils.use_user_library())
        ProcessingConfig.setSettingValue(RUtils.R_USE_USER_LIB, False)
        self.assertFalse(RUtils.use_user_library())
        ProcessingConfig.setSettingValue(RUtils.R_USE_USER_LIB, True)
        self.assertTrue(RUtils.use_user_library())

    def test_library_folder(self):
        """
        Test retrieving/setting the library folder
        """
        self.assertIn('/profiles/default/processing/rlibs', RUtils.r_library_folder())
        ProcessingConfig.setSettingValue(RUtils.R_LIBS_USER, '/usr/local')
        self.assertEqual(RUtils.r_library_folder(), '/usr/local')
        ProcessingConfig.setSettingValue(RUtils.R_LIBS_USER, None)
        self.assertIn('/profiles/default/processing/rlibs', RUtils.r_library_folder())

    def test_is_error_line(self):
        """
        Test is_error_line
        """
        self.assertFalse(RUtils.is_error_line('xxx yyy'))
        self.assertTrue(RUtils.is_error_line('Error something went wrong'))
        self.assertTrue(RUtils.is_error_line('Execution halted'))

    def test_r_is_installed(self):
        """
        Test checking that R is installed
        """
        self.assertIsNone(RUtils.check_r_is_installed())
        ProcessingConfig.setSettingValue(RUtils.R_FOLDER, '/home')
        self.assertTrue(RUtils.check_r_is_installed())
        self.assertIn('R is not installed', RUtils.check_r_is_installed())
        ProcessingConfig.setSettingValue(RUtils.R_FOLDER, None)
        self.assertIsNone(RUtils.check_r_is_installed())

    def test_is_valid_r_variable(self):
        """
        Test for strings to check if they are valid R variables.
        """
        self.assertFalse(RUtils.is_valid_r_variable("var_name%"))
        self.assertFalse(RUtils.is_valid_r_variable("2var_name"))
        self.assertFalse(RUtils.is_valid_r_variable(".2var_name"))
        self.assertFalse(RUtils.is_valid_r_variable("_var_name"))
        self.assertTrue(RUtils.is_valid_r_variable("var_name2."))
        self.assertTrue(RUtils.is_valid_r_variable(".var_name"))
        self.assertTrue(RUtils.is_valid_r_variable("var.name"))


if __name__ == "__main__":
    suite = unittest.makeSuite(RUtilsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
