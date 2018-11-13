# -*- coding: utf-8 -*-

"""
***************************************************************************
    utils.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from builtins import str
from builtins import object

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import re
import os
import stat
import subprocess

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsSettings,
                       QgsProcessingUtils)
from processing.core.ProcessingConfig import ProcessingConfig
from processing.tools.system import userFolder, isWindows, mkdir


class RUtils(object):
    RSCRIPTS_FOLDER = 'R_SCRIPTS_FOLDER'
    R_FOLDER = 'R_FOLDER'
    R_USE64 = 'R_USE64'
    R_LIBS_USER = 'R_LIBS_USER'

    VALID_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    R_INSTALLED_SETTINGS_PATH = 'r/r_installed'

    rscriptfilename = os.path.join(userFolder(), 'processing_script.r')

    consoleResults = []
    allConsoleResults = []

    @staticmethod
    def RFolder():
        folder = ProcessingConfig.getSetting(RUtils.R_FOLDER)
        if folder is None:
            if isWindows():
                if 'ProgramW6432' in list(os.environ.keys()) and os.path.isdir(
                        os.path.join(os.environ['ProgramW6432'], 'R')):
                    testfolder = os.path.join(os.environ['ProgramW6432'], 'R')
                elif 'PROGRAMFILES(x86)' in list(os.environ.keys()) and os.path.isdir(
                        os.path.join(os.environ['PROGRAMFILES(x86)'], 'R')):
                    testfolder = os.path.join(os.environ['PROGRAMFILES(x86)'], 'R')
                elif 'PROGRAMFILES' in list(os.environ.keys()) and os.path.isdir(
                        os.path.join(os.environ['PROGRAMFILES'], 'R')):
                    testfolder = os.path.join(os.environ['PROGRAMFILES'], 'R')
                else:
                    testfolder = 'C:\\R'

                if os.path.isdir(testfolder):
                    subfolders = os.listdir(testfolder)
                    subfolders.sort(reverse=True)
                    for subfolder in subfolders:
                        if subfolder.startswith('R-'):
                            folder = os.path.join(testfolder, subfolder)
                            break
                else:
                    folder = ''
            else:
                folder = ''

        return os.path.abspath(str(folder))

    @staticmethod
    def RLibs():
        folder = ProcessingConfig.getSetting(RUtils.R_LIBS_USER)
        if folder is None:
            folder = str(os.path.join(userFolder(), 'rlibs'))
        try:
            mkdir(folder)
        except:
            folder = str(os.path.join(userFolder(), 'rlibs'))
            mkdir(folder)
        return os.path.abspath(str(folder))

    @staticmethod
    def builtin_scripts_folder():
        """
        Returns the built-in scripts path
        """
        return os.path.join(os.path.dirname(__file__), '..', 'builtin_scripts')

    @staticmethod
    def default_scripts_folder():
        """
        Returns the default path to look for user scripts within
        """
        folder = os.path.join(userFolder(), 'rscripts')
        mkdir(folder)
        return os.path.abspath(folder)

    @staticmethod
    def script_folders():
        """
        Returns a list of folders to search for scripts within
        """
        folder = ProcessingConfig.getSetting(RUtils.RSCRIPTS_FOLDER)
        if folder is not None:
            folders = folder.split(';')
        else:
            folders = [RUtils.default_scripts_folder()]

        folders.append(RUtils.builtin_scripts_folder())
        return folders

    @staticmethod
    def create_descriptive_name(name):
        """
        Returns a safe version of a parameter name
        """
        return name.replace('_', ' ')

    @staticmethod
    def strip_special_characters(name):
        """
        Strips non-alphanumeric characters from a name
        """
        return ''.join(c for c in name if c in RUtils.VALID_CHARS)

    @staticmethod
    def createRScriptFromRCommands(commands):
        with open(RUtils.getRScriptFilename(), 'w') as scriptfile:
            for command in commands:
                scriptfile.write(command + '\n')

    @staticmethod
    def getRScriptFilename():
        return RUtils.rscriptfilename

    @staticmethod
    def getConsoleOutputFilename():
        return RUtils.getRScriptFilename() + '.Rout'

    @staticmethod
    def execute_r_algorithm(alg, parameters, context, feedback):
        """
        Runs a prepared algorithm in R
        """

        # generate new R script file name in a temp folder
        RUtils.rscriptfilename = QgsProcessingUtils.generateTempFilename('processing_script.r')
        # run commands
        RUtils.verboseCommands = alg.getVerboseCommands()
        RUtils.createRScriptFromRCommands(alg.build_r_script(parameters, context, feedback))
        if isWindows():
            if ProcessingConfig.getSetting(RUtils.R_USE64):
                execDir = 'x64'
            else:
                execDir = 'i386'
            command = [
                os.path.join(RUtils.RFolder(), 'bin', execDir, 'R.exe'),
                'CMD',
                'BATCH',
                '--vanilla',
                RUtils.getRScriptFilename(),
                RUtils.getConsoleOutputFilename()
            ]

        else:
            os.chmod(RUtils.getRScriptFilename(), stat.S_IEXEC | stat.S_IREAD |
                     stat.S_IWRITE)
            command = 'R CMD BATCH --vanilla ' + RUtils.getRScriptFilename() \
                      + ' ' + RUtils.getConsoleOutputFilename()

        proc = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        proc.wait()
        RUtils.createConsoleOutput()
        loglines = []
        loglines.append(RUtils.tr('R execution console output'))
        loglines += RUtils.allConsoleResults
        for line in loglines:
            feedback.pushConsoleInfo(line)

    @staticmethod
    def createConsoleOutput():
        RUtils.consoleResults = []
        RUtils.allConsoleResults = []
        add = False
        if os.path.exists(RUtils.getConsoleOutputFilename()):
            with open(RUtils.getConsoleOutputFilename()) as lines:
                for line in lines:
                    line = line.strip().strip(' ')
                    if line.startswith('>'):
                        line = line[1:].strip(' ')
                        if line in RUtils.verboseCommands:
                            add = True
                        else:
                            add = False
                    elif add:
                        RUtils.consoleResults.append('<p>' + line + '</p>\n')
                    RUtils.allConsoleResults.append(line)

    @staticmethod
    def getConsoleOutput():
        s = '<font face="courier">\n'
        s += RUtils.tr('<h2>R Output</h2>\n')
        for line in RUtils.consoleResults:
            s += line
        s += '</font>\n'

        return s

    @staticmethod
    def check_r_is_installed(ignore_registry_settings=False):
        if isWindows():
            path = RUtils.RFolder()
            if path == '':
                return RUtils.tr('R folder is not configured.\nPlease configure '
                                 'it before running R scripts.')

        settings = QgsSettings()
        if not ignore_registry_settings:
            if settings.value(RUtils.R_INSTALLED_SETTINGS_PATH, False, bool, QgsSettings.Plugins):
                return

        if isWindows():
            if ProcessingConfig.getSetting(RUtils.R_USE64):
                execDir = 'x64'
            else:
                execDir = 'i386'
            command = [os.path.join(RUtils.RFolder(), 'bin', execDir, 'R.exe'), '--version']
        else:
            command = ['R --version']

        with subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        ) as proc:
            for line in proc.stdout:
                if 'R version' in line:
                    settings.setValue(RUtils.R_INSTALLED_SETTINGS_PATH, True, QgsSettings.Plugins)
                    return

        html = RUtils.tr(
            '<p>This algorithm requires R to be run. Unfortunately, it '
            'seems that R is not installed in your system, or it is not '
            'correctly configured to be used from QGIS</p>'
            '<p><a href="http://docs.qgis.org/testing/en/docs/user_manual/processing/3rdParty.html">Click here</a> '
            'to know more about how to install and configure R to be used with QGIS</p>')

        return html

    @staticmethod
    def getRequiredPackages(code):
        regex = re.compile('[^#]library\("?(.*?)"?\)')
        return regex.findall(code)

    @staticmethod
    def tr(string, context=''):
        if context == '':
            context = 'RUtils'
        return QCoreApplication.translate(context, string)
