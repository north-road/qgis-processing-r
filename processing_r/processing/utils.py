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
import platform
import subprocess
import sys
from typing import Optional
from ctypes import cdll

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessingUtils,
                       QgsMessageLog,
                       Qgis)
from processing.core.ProcessingConfig import ProcessingConfig
from processing.tools.system import userFolder, mkdir

DEBUG = True


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

    @staticmethod
    def is_windows() -> bool:
        """
        Returns True if the plugin is running on Windows
        """
        return os.name == 'nt'

    @staticmethod
    def is_macos() -> bool:
        """
        Returns True if the plugin is running on MacOS
        """
        return platform.system() == 'Darwin'

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
        if RUtils.is_macos():
            return '/usr/local/bin'

        if RUtils.is_windows():
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

        # expect R to be in OS path
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
    def is_valid_r_variable(variable: str) -> bool:
        """
        Check if given string is valid R variable name.
        :param variable: string
        :return: bool
        """

        # only letters a-z, A-Z, numbers, dot and underscore
        x = re.search("[a-zA-Z0-9\\._]+", variable)

        result = True

        if variable == x.group():
            # cannot start with number or underscore, or start with dot followed by number
            x = re.search("^[0-9|_]|^\\.[0-9]", variable)
            if x:
                result = False
        else:
            result = False

        return result

    @staticmethod
    def strip_special_characters(name):
        """
        Strips non-alphanumeric characters from a name
        """
        return ''.join(c for c in name if c in RUtils.VALID_CHARS)

    @staticmethod
    def create_r_script_from_commands(commands):
        """
        Creates an R script in a temporary location consisting of the given commands.
        Returns the path to the temporary script file.
        """
        script_file = QgsProcessingUtils.generateTempFilename('processing_script.r')
        with open(script_file, 'w') as f:
            for command in commands:
                f.write(command + '\n')
        return script_file

    @staticmethod
    def is_error_line(line):
        """
        Returns True if the given line looks like an error message
        """
        return any([error in line for error in ['Error ', 'Execution halted']])

    @staticmethod
    def get_windows_code_page():
        """
        Determines MS-Windows CMD.exe shell codepage.
        Used into GRASS exec script under MS-Windows.
        """
        return str(cdll.kernel32.GetACP())

    @staticmethod
    def get_process_startup_info():
        """
        Returns the correct startup info to use when calling commands for different platforms
        """
        # For MS-Windows, we need to hide the console window.
        si = None
        if RUtils.is_windows():
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
        return si

    @staticmethod
    def get_process_keywords():
        """
        Returns the correct process keywords dict to use when calling commands for different platforms
        """
        kw = {}
        if RUtils.is_windows():
            kw['startupinfo'] = RUtils.get_process_startup_info()
            if sys.version_info >= (3, 6):
                kw['encoding'] = "cp{}".format(RUtils.get_windows_code_page())
        return kw

    @staticmethod
    def execute_r_algorithm(alg, parameters, context, feedback):
        """
        Runs a prepared algorithm in R, and returns a list of the output received from R
        """
        # generate new R script file name in a temp folder

        script_lines = alg.build_r_script(parameters, context, feedback)
        for line in script_lines:
            feedback.pushCommandInfo(line)

        script_filename = RUtils.create_r_script_from_commands(script_lines)

        # run commands
        command = [
            RUtils.path_to_r_executable(script_executable=True),
            script_filename
        ]

        feedback.pushInfo(RUtils.tr('R execution console output'))

        console_results = list()

        with subprocess.Popen(command,
                              stdout=subprocess.PIPE,
                              stdin=subprocess.DEVNULL,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True,
                              **RUtils.get_process_keywords()
                              ) as proc:
            for line in iter(proc.stdout.readline, ''):
                if feedback.isCanceled():
                    proc.terminate()

                if RUtils.is_error_line(line):
                    feedback.reportError(line.strip())
                else:
                    feedback.pushConsoleInfo(line.strip())
                console_results.append(line.strip())
        return console_results

    @staticmethod
    def html_formatted_console_output(output):
        """
        Returns a HTML formatted string of the given output lines
        """
        s = '<h2>{}</h2>\n'.format(RUtils.tr('R Output'))
        s += '<code>\n'
        for line in output:
            s += '{}<br />\n'.format(line)
        s += '</code>'
        return s

    @staticmethod
    def path_to_r_executable(script_executable=False) -> str:
        """
        Returns the path to the R executable
        """
        executable = 'Rscript' if script_executable else 'R'
        bin_folder = RUtils.r_binary_folder()
        if bin_folder:
            if RUtils.is_windows():
                if ProcessingConfig.getSetting(RUtils.R_USE64):
                    exec_dir = 'x64'
                else:
                    exec_dir = 'i386'
                return os.path.join(bin_folder, 'bin', exec_dir, '{}.exe'.format(executable))
            return os.path.join(bin_folder, executable)

        return executable

    @staticmethod
    def check_r_is_installed() -> Optional[str]:
        """
        Checks if R is installed and working. Returns None if R IS working,
        or an error string if R was not found.
        """
        if DEBUG:
            QgsMessageLog.logMessage(RUtils.tr('R binary path: {}').format(RUtils.path_to_r_executable()), 'R',
                                     Qgis.Info)

        if RUtils.is_windows():
            path = RUtils.r_binary_folder()
            if path == '':
                return RUtils.tr('R folder is not configured.\nPlease configure '
                                 'it before running R scripts.')

        command = [RUtils.path_to_r_executable(), '--version']
        try:
            with subprocess.Popen(command,
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.DEVNULL,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  **RUtils.get_process_keywords()) as proc:
                for line in proc.stdout:
                    if ('R version' in line) or ('R Under development' in line):
                        return None
        except FileNotFoundError:
            pass

        html = RUtils.tr(
            '<p>This algorithm requires R to be run. Unfortunately, it '
            'seems that R is not installed in your system, or it is not '
            'correctly configured to be used from QGIS</p>'
            '<p><a href="http://docs.qgis.org/testing/en/docs/user_manual/processing/3rdParty.html">Click here</a> '
            'to know more about how to install and configure R to be used with QGIS</p>')

        return html

    @staticmethod
    def get_r_version() -> Optional[str]:
        """
        Returns the current installed R version, or None if R is not found
        """
        if RUtils.is_windows() and not RUtils.r_binary_folder():
            return None

        command = [RUtils.path_to_r_executable(), '--version']
        try:
            with subprocess.Popen(command,
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.DEVNULL,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  **RUtils.get_process_keywords()) as proc:
                for line in proc.stdout:
                    if ('R version' in line) or ('R Under development' in line):
                        return line
        except FileNotFoundError:
            pass

        return None

    @staticmethod
    def get_required_packages(code):
        """
        Returns a list of the required packages
        """
        regex = re.compile(r'[^#]library\("?(.*?)"?\)')
        return regex.findall(code)

    @staticmethod
    def upgrade_parameter_line(line: str) -> str:
        """
        Upgrades a parameter definition line from 2.x to 3.x format
        """
        # alias 'selection' to 'enum'
        if '=selection' in line:
            line = line.replace('=selection', '=enum')
        if '=vector' in line:
            line = line.replace('=vector', '=source')
        return line

    @staticmethod
    def tr(string, context=''):
        """
        Translates a string
        """
        if context == '':
            context = 'RUtils'
        return QCoreApplication.translate(context, string)
