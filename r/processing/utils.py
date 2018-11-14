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
import re
import os
import stat
import subprocess
from typing import Optional

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingUtils
from processing.core.ProcessingConfig import ProcessingConfig
from processing.tools.system import userFolder, mkdir


class RUtils:  # pylint: disable=too-many-public-methods
    """
    Utilities for the R Provider and Algorithm
    """

    RSCRIPTS_FOLDER = 'R_SCRIPTS_FOLDER'
    R_FOLDER = 'R_FOLDER'
    R_USE64 = 'R_USE64'
    R_LIBS_USER = 'R_LIBS_USER'
    R_USE_USER_LIB = 'R_USE_USER_LIB'
    R_REPO = 'R_REPO'

    VALID_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    rscriptfilename = os.path.join(userFolder(), 'processing_script.r')

    consoleResults = []
    allConsoleResults = []

    @staticmethod
    def is_windows() -> bool:
        """
        Returns True if the plugin is running on Windows
        """
        return os.name == 'nt'

    @staticmethod
    def r_binary_folder() -> str:
        """
        Returns the folder (hopefully) containing R binaries
        """
        folder = ProcessingConfig.getSetting(RUtils.R_FOLDER)
        if not folder:
            folder = RUtils.guess_r_binary_folder()

        return os.path.abspath(folder) if folder else ''

    @staticmethod
    def guess_r_binary_folder() -> str:
        """
        Tries to pick a reasonable path for the R binaries to be executed from
        """
        if not RUtils.is_windows():
            # expect R to be in OS path
            return ''

        search_paths = ['ProgramW6432', 'PROGRAMFILES(x86)', 'PROGRAMFILES', 'C:\\']
        r_folder = ''
        for path in search_paths:
            if path in os.environ and os.path.isdir(
                    os.path.join(os.environ[path], 'R')):
                r_folder = os.path.join(os.environ[path], 'R')
                break

        if r_folder:
            sub_folders = os.listdir(r_folder)
            sub_folders.sort(reverse=True)
            for sub_folder in sub_folders:
                if sub_folder.upper().startswith('R-'):
                    return os.path.join(r_folder, sub_folder)

        # not found!
        return ''

    @staticmethod
    def package_repo():
        """
        Returns the package repo URL
        """
        return ProcessingConfig.getSetting(RUtils.R_REPO)

    @staticmethod
    def use_user_library():
        """
        Returns True if user library folder should be used instead of system folder
        """
        return ProcessingConfig.getSetting(RUtils.R_USE_USER_LIB)

    @staticmethod
    def r_library_folder():
        """
        Returns the user R library folder
        """
        folder = ProcessingConfig.getSetting(RUtils.R_LIBS_USER)
        if folder is None:
            folder = str(os.path.join(userFolder(), 'rlibs'))
        try:
            mkdir(folder)
        except FileNotFoundError:
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
    def is_error_line(line):
        """
        Returns True if the given line looks like an error message
        """
        return any([l in line for l in ['Error ', 'Execution halted']])

    @staticmethod
    def get_windows_code_page():
        """
        Determines MS-Windows CMD.exe shell codepage.
        Used into GRASS exec script under MS-Windows.
        """
        from ctypes import cdll
        return str(cdll.kernel32.GetACP())

    @staticmethod
    def execute_r_algorithm(alg, parameters, context, feedback):
        """
        Runs a prepared algorithm in R
        """

        # generate new R script file name in a temp folder
        RUtils.rscriptfilename = QgsProcessingUtils.generateTempFilename('processing_script.r')
        # run commands
        RUtils.verboseCommands = alg.get_script_body_commands()
        RUtils.createRScriptFromRCommands(alg.build_r_script(parameters, context, feedback))
        if not RUtils.is_windows():
            os.chmod(RUtils.getRScriptFilename(), stat.S_IEXEC | stat.S_IREAD |
                     stat.S_IWRITE)

        command = [
            RUtils.path_to_r_executable(),
            RUtils.getRScriptFilename()
        ]

        feedback.pushInfo(RUtils.tr('R execution console output'))

        # For MS-Windows, we need to hide the console window.
        si = None
        if RUtils.is_windows():
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE

        RUtils.consoleResults = []

        with subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                encoding="cp{}".format(RUtils.get_windows_code_page()) if RUtils.is_windows() else None,
                startupinfo=si if RUtils.is_windows() else None,
                universal_newlines=True
        ) as proc:
            for line in iter(proc.stdout.readline, ''):
                if RUtils.is_error_line(line):
                    feedback.reportError(line.strip())
                else:
                    feedback.pushConsoleInfo(line.strip())
                RUtils.consoleResults.append('<p>' + line.strip() + '</p>\n')

    @staticmethod
    def getConsoleOutput():
        s = '<font face="courier">\n'
        s += RUtils.tr('<h2>R Output</h2>\n')
        for line in RUtils.consoleResults:
            s += line
        s += '</font>\n'

        return s

    @staticmethod
    def path_to_r_executable() -> str:
        """
        Returns the path to the R executable
        """
        bin_folder = RUtils.r_binary_folder()
        if bin_folder:
            if RUtils.is_windows():
                if ProcessingConfig.getSetting(RUtils.R_USE64):
                    exec_dir = 'x64'
                else:
                    exec_dir = 'i386'
                return os.path.join(bin_folder, 'bin', exec_dir, 'Rscript.exe')
            else:
                return os.path.join(bin_folder, 'Rscript')

        return 'Rscript'

    @staticmethod
    def check_r_is_installed() -> Optional[str]:
        if RUtils.is_windows():
            path = RUtils.r_binary_folder()
            if path == '':
                return RUtils.tr('R folder is not configured.\nPlease configure '
                                 'it before running R scripts.')

        command = ['{} --version'.format(RUtils.path_to_r_executable())]

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
                    return None

        html = RUtils.tr(
            '<p>This algorithm requires R to be run. Unfortunately, it '
            'seems that R is not installed in your system, or it is not '
            'correctly configured to be used from QGIS</p>'
            '<p><a href="http://docs.qgis.org/testing/en/docs/user_manual/processing/3rdParty.html">Click here</a> '
            'to know more about how to install and configure R to be used with QGIS</p>')

        return html

    @staticmethod
    def get_required_packages(code):
        """
        Returns a list of the required packages
        """
        regex = re.compile(r'[^#]library\("?(.*?)"?\)')
        return regex.findall(code)

    @staticmethod
    def tr(string, context=''):
        """
        Translates a string
        """
        if context == '':
            context = 'RUtils'
        return QCoreApplication.translate(context, string)
