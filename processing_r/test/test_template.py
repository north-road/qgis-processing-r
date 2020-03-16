# coding=utf-8
"""R templates Test.

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
from processing_r.processing.r_templates import RTemplates
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()

test_data_path = os.path.join(
    os.path.dirname(__file__),
    'data')


class TemplateTest(unittest.TestCase):
    """Test template generation."""

    def testGithubInstall(self):
        """
        Test github install code generation.
        """
        templates = RTemplates()
        templates.install_github = True
        templates.github_dependencies = "user_1/repo_1, user_2/repo_2"
        self.assertEqual(templates.install_package_github(templates.github_dependencies[0]),
                         'remotes::install_github("user_1/repo_1")')
        self.assertEqual(templates.install_package_github(templates.github_dependencies[1]),
                         'remotes::install_github("user_2/repo_2")')

    def testString(self):  # pylint: disable=too-many-locals,too-many-statements
        """
        Test string variable
        """
        templates = RTemplates()
        self.assertEqual(templates.set_variable_string('var', 'val'), 'var <- "val"')
        self.assertEqual(templates.set_variable_string('var', 'va"l'), 'var <- "va\\"l"')

    def testStringListVariable(self):  # pylint: disable=too-many-locals,too-many-statements
        """
        Test string list variable
        """
        templates = RTemplates()
        self.assertEqual(templates.set_variable_string_list('var', []), 'var <- c()')
        self.assertEqual(templates.set_variable_string_list('var', ['aaaa']), 'var <- c("aaaa")')
        self.assertEqual(templates.set_variable_string_list('var', ['aaaa', 'va"l']), 'var <- c("aaaa","va\\"l")')


if __name__ == "__main__":
    suite = unittest.makeSuite(TemplateTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
