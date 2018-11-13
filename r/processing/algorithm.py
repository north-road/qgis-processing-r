# -*- coding: utf-8 -*-

"""
***************************************************************************
    algorithm.py
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
from future import standard_library
standard_library.install_aliases()
from builtins import str

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import json

from qgis.core import (QgsApplication,
                       QgsMessageLog,
                       QgsProcessingAlgorithm)
from qgis.PyQt.QtCore import QCoreApplication
#
# from processing.gui.Help2Html import getHtmlFromHelpFile
# from processing.core.parameters import ParameterRaster
# from processing.core.parameters import ParameterTable
# from processing.core.parameters import ParameterVector
# from processing.core.parameters import ParameterMultipleInput
# from processing.core.parameters import ParameterString
# from processing.core.parameters import ParameterNumber
# from processing.core.parameters import ParameterBoolean
# from processing.core.parameters import ParameterSelection
# from processing.core.parameters import ParameterTableField
# from processing.core.parameters import ParameterExtent
# from processing.core.parameters import ParameterCrs
# from processing.core.parameters import ParameterFile
# from processing.core.outputs import OutputTable
# from processing.core.outputs import OutputVector
# from processing.core.outputs import OutputRaster
# from processing.core.outputs import OutputHTML
# from processing.core.parameters import getParameterFromString
# from processing.core.outputs import getOutputFromString
# from processing.tools import dataobjects
# from processing.tools.system import isWindows
# from processing.script.WrongScriptException import WrongScriptException
from r.processing.exceptions import InvalidScriptException
from r.processing.utils import RUtils
from r.gui.gui_utils import GuiUtils


class RAlgorithm(QgsProcessingAlgorithm):

    R_CONSOLE_OUTPUT = 'R_CONSOLE_OUTPUT'
    RPLOTS = 'RPLOTS'

    def __init__(self, description_file, script=None):
        super().__init__()

        self.script = script
        self._name = ''
        self._display_name = ''
        self._group = ''
        self.description_file = description_file
        self.error = None
        self.commands = []

        if script is not None:
            self.load_from_string()
        if description_file is not None:
            self.load_from_file()

    def createInstance(self):
        if self.description_file is not None:
            return RAlgorithm(self.description_file)
        else:
            return RAlgorithm(description_file=None, script=self.script)

    def initAlgorithm(self, config=None):
        pass

    def icon(self):
        return GuiUtils.get_icon("providerR.svg")

    def svgIconPath(self):
        return GuiUtils.get_icon_svg("providerR.svg")

    def name(self):
        return self._name

    def displayName(self):
        return self._display_name

    def group(self):
        return self._group

    def load_from_string(self):
        """
        Load the algorithm from a string
        """
        lines = self.script.split('\n')
        self._name = 'unnamedalgorithm'
        self._display_name = self.tr('[Unnamed algorithm]')
        self._group = self.tr('User R scripts')
        self.parse_script(iter(lines))

    def load_from_file(self):
        """
        Load the algorithm from a file
        """
        filename = os.path.basename(self.description_file)
        self._name = filename[:filename.rfind('.')].replace('_', ' ')
        self._group = self.tr('User R scripts')
        with open(self.description_file, 'r') as f:
            lines = [line.strip() for line in f]
        self.parse_script(iter(lines))

    def parse_script(self, lines):
        self.script = ''
        self.commands = []
        self.error = None
        #self.showPlots = False
        #self.showConsoleOutput = False
        #self.useRasterPackage = True
        #self.passFileNames = False
        ender = 0
        line = next(lines).strip('\n').strip('\r')
        while ender < 10:
            if line.startswith('##'):
                try:
                    self.processParameterLine(line)
                except Exception:
                    self.error = self.tr('This script has a syntax error.\n'
                                         'Problem with line: {0}').format(line)
            elif line.startswith('>'):
                self.commands.append(line[1:])
                #if not self.showConsoleOutput:
                #    self.addOutput(OutputHTML(RAlgorithm.R_CONSOLE_OUTPUT,
                #                              self.tr('R Console Output')))
                #self.showConsoleOutput = True
            else:
                if line == '':
                    ender += 1
                else:
                    ender = 0
                self.commands.append(line)
            self.script += line + '\n'
            try:
                line = next(lines).strip('\n').strip('\r')
            except:
                break

    def createDescriptiveName(self, s):
        return s.replace('_', ' ')

    def processParameterLine(self, line):
        return
        #
        #param = None
        #line = line.replace('#', '')
        #if line.lower().strip().startswith('showplots'):
        #    self.showPlots = True
        #    self.addOutput(OutputHTML(RAlgorithm.RPLOTS, 'R Plots'))
        #    return
        #if line.lower().strip().startswith('dontuserasterpackage'):
        #    self.useRasterPackage = False
        #    return
        #if line.lower().strip().startswith('passfilenames'):
        #    self.passFileNames = True
        #    return
        #tokens = line.split('=')
        #desc = self.createDescriptiveName(tokens[0])
        #if tokens[1].lower().strip() == 'group':
        #    self._group = tokens[0]
        #    return
        #if tokens[1].lower().strip() == 'name':
        #    self._name = self._display_name = tokens[0]
        #    self._name = self._name.lower()
        #    validChars = \
        #        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:'
        #    self._name = ''.join(c for c in self._name if c in validChars)
        #    return
#
        #out = getOutputFromString(line)
        #if out is None:
        #    param = getParameterFromString(line)
#
        #if param is not None:
        #    self.addParameter(param)
        #elif out is not None:
        #    out.name = tokens[0]
        #    out.description = desc
        #    self.addOutput(out)
        #else:
        #    raise WrongScriptException(
        #        self.tr('Could not load script: {0}.\n'
        #                'Problem with line "{1}"', 'ScriptAlgorithm').format(self.descriptionFile or '', line))
#
        #    raise WrongScriptException(
        #        self.tr('Could not load R script: {0}.\n Problem with line {1}').format(self.descriptionFile, line))

    def canExecute(self):
        return not self.error, self.error

    def processAlgorithm(self, parameters, context, feedback):
        return {}#
        #if isWindows():
        #    path = RUtils.RFolder()
        #    if path == '':
        #        raise GeoAlgorithmExecutionException(
        #            self.tr('R folder is not configured.\nPlease configure it '
        #                    'before running R scripts.'))
        #loglines = []
        #loglines.append(self.tr('R execution commands'))
        #loglines += self.getFullSetOfRCommands()
        #for line in loglines:
        #    feedback.pushCommandInfo(line)
        #QgsMessageLog.logMessage(loglines, self.tr('Processing'), QgsMessageLog.INFO)
        #RUtils.executeRAlgorithm(self, feedback)
        #if self.showPlots:
        #    htmlfilename = self.getOutputValue(RAlgorithm.RPLOTS)
        #    with open(htmlfilename, 'w') as f:
        #        f.write('<html><img src="' + self.plotsFilename + '"/></html>')
        #if self.showConsoleOutput:
        #    htmlfilename = self.getOutputValue(RAlgorithm.R_CONSOLE_OUTPUT)
        #    with open(htmlfilename, 'w') as f:
        #        f.write(RUtils.getConsoleOutput())

    def getFullSetOfRCommands(self):
        commands = []
        commands += self.getImportCommands()
        commands += self.getRCommands()
        commands += self.getExportCommands()

        return commands

    def getExportCommands(self):
        commands = []
        for out in self.outputs:
            if isinstance(out, OutputRaster):
                value = out.value
                value = value.replace('\\', '/')
                if self.useRasterPackage or self.passFileNames:
                    commands.append('writeRaster(' + out.name + ',"' + value +
                                    '", overwrite=TRUE)')
                else:
                    if not value.endswith('tif'):
                        value = value + '.tif'
                    commands.append('writeGDAL(' + out.name + ',"' + value +
                                    '")')
            elif isinstance(out, OutputVector):
                value = out.value
                if not value.endswith('shp'):
                    value = value + '.shp'
                value = value.replace('\\', '/')
                filename = os.path.basename(value)
                filename = filename[:-4]
                commands.append('writeOGR(' + out.name + ',"' + value + '","' +
                                filename + '", driver="ESRI Shapefile")')
            elif isinstance(out, OutputTable):
                value = out.value
                value = value.replace('\\', '/')
                commands.append('write.csv(' + out.name + ',"' + value + '")')

        if self.showPlots:
            commands.append('dev.off()')

        return commands

    def getImportCommands(self):
        commands = []

        # Just use main mirror
        commands.append('options("repos"="http://cran.at.r-project.org/")')

        # Try to install packages if needed
        if isWindows():
            commands.append('.libPaths(\"' + str(RUtils.RLibs()).replace('\\', '/') + '\")')
        packages = RUtils.getRequiredPackages(self.script)
        packages.extend(['rgdal', 'raster'])
        for p in packages:
            commands.append('tryCatch(find.package("' + p +
                            '"), error=function(e) install.packages("' + p +
                            '", dependencies=TRUE))')
        commands.append('library("raster")')
        commands.append('library("rgdal")')

        for param in self.parameters:
            if isinstance(param, ParameterRaster):
                if param.value is None:
                    commands.append(param.name + '= NULL')
                else:
                    value = param.value
                    value = value.replace('\\', '/')
                    if self.passFileNames:
                        commands.append(param.name + ' = "' + value + '"')
                    elif self.useRasterPackage:
                        commands.append(param.name + ' = ' + 'brick("' + value + '")')
                    else:
                        commands.append(param.name + ' = ' + 'readGDAL("' + value + '")')
            elif isinstance(param, ParameterVector):
                if param.value is None:
                    commands.append(param.name + '= NULL')
                else:
                    value = param.getSafeExportedLayer()
                    value = value.replace('\\', '/')
                    filename = os.path.basename(value)
                    filename = filename[:-4]
                    folder = os.path.dirname(value)
                    if self.passFileNames:
                        commands.append(param.name + ' = "' + value + '"')
                    else:
                        commands.append(param.name + ' = readOGR("' + folder +
                                        '",layer="' + filename + '")')
            elif isinstance(param, ParameterTable):
                if param.value is None:
                    commands.append(param.name + '= NULL')
                else:
                    value = param.value
                    if not value.lower().endswith('csv'):
                        raise GeoAlgorithmExecutionException(
                            'Unsupported input file format.\n' + value)
                    if self.passFileNames:
                        commands.append(param.name + ' = "' + value + '"')
                    else:
                        commands.append(param.name + ' <- read.csv("' + value +
                                        '", head=TRUE, sep=",")')
            elif isinstance(param, ParameterExtent):
                if param.value:
                    tokens = str(param.value).split(',')
                    # Extent from raster package is "xmin, xmax, ymin, ymax" like in Processing
                    # http://www.inside-r.org/packages/cran/raster/docs/Extent
                    commands.append(param.name + ' = extent(' + tokens[0] + ',' + tokens[1] + ',' + tokens[2] + ',' + tokens[3] + ')')
                else:
                    commands.append(param.name + ' = NULL')
            elif isinstance(param, ParameterCrs):
                if param.value is None:
                    commands.append(param.name + '= NULL')
                else:
                    commands.append(param.name + ' = "' + param.value + '"')
            elif isinstance(param, (ParameterTableField, ParameterString, ParameterFile)):
                if param.value is None:
                    commands.append(param.name + '= NULL')
                else:
                    commands.append(param.name + '="' + param.value + '"')
            elif isinstance(param, (ParameterNumber, ParameterSelection)):
                if param.value is None:
                    commands.append(param.name + '= NULL')
                else:
                    commands.append(param.name + '=' + str(param.value))
            elif isinstance(param, ParameterBoolean):
                if param.value:
                    commands.append(param.name + '=TRUE')
                else:
                    commands.append(param.name + '=FALSE')
            elif isinstance(param, ParameterMultipleInput):
                iLayer = 0
                if param.datatype == dataobjects.TYPE_RASTER:
                    layers = param.value.split(';')
                    for layer in layers:
                        layer = layer.replace('\\', '/')
                        if self.passFileNames:
                            commands.append('tempvar' + str(iLayer) + ' <- "' +
                                            layer + '"')
                        elif self.useRasterPackage:
                            commands.append('tempvar' + str(iLayer) + ' <- ' +
                                            'brick("' + layer + '")')
                        else:
                            commands.append('tempvar' + str(iLayer) + ' <- ' +
                                            'readGDAL("' + layer + '")')
                        iLayer += 1
                else:
                    exported = param.getSafeExportedLayers()
                    layers = exported.split(';')
                    for layer in layers:
                        if not layer.lower().endswith('shp') \
                           and not self.passFileNames:
                            raise GeoAlgorithmExecutionException(
                                'Unsupported input file format.\n' + layer)
                        layer = layer.replace('\\', '/')
                        filename = os.path.basename(layer)
                        filename = filename[:-4]
                        if self.passFileNames:
                            commands.append('tempvar' + str(iLayer) + ' <- "' +
                                            layer + '"')
                        else:
                            commands.append('tempvar' + str(iLayer) + ' <- ' +
                                            'readOGR("' + layer + '",layer="' +
                                            filename + '")')
                        iLayer += 1
                s = ''
                s += param.name
                s += ' = c('
                iLayer = 0
                for layer in layers:
                    if iLayer != 0:
                        s += ','
                    s += 'tempvar' + str(iLayer)
                    iLayer += 1
                s += ')\n'
                commands.append(s)

        if self.showPlots:
            htmlfilename = self.getOutputValue(RAlgorithm.RPLOTS)
            self.plotsFilename = htmlfilename + '.png'
            self.plotsFilename = self.plotsFilename.replace('\\', '/')
            commands.append('png("' + self.plotsFilename + '")')

        return commands

    def getRCommands(self):
        return self.commands

   # def help(self):
   #     helpfile = str(self.descriptionFile) + '.help'
   #     if os.path.exists(helpfile):
   #         return True, getHtmlFromHelpFile(self, helpfile)
   #     else:
   #         return False, None
#
   # def shortHelp(self):
   #     if self.descriptionFile is None:
   #         return None
   #     helpFile = str(self.descriptionFile) + '.help'
   #     if os.path.exists(helpFile):
   #         with open(helpFile) as f:
   #             try:
   #                 descriptions = json.load(f)
   #                 if 'ALG_DESC' in descriptions:
   #                     return self._formatHelp(str(descriptions['ALG_DESC']))
   #             except:
   #                 return None
   #     return None
#
    def getParameterDescriptions(self):#
        descs = {}
        if self.descriptionFile is None:
            return descs
        helpFile = str(self.descriptionFile) + '.help'
        if os.path.exists(helpFile):
            with open(helpFile) as f:
                try:
                    descriptions = json.load(f)
                    for param in self.parameters:
                        if param.name in descriptions:
                            descs[param.name] = str(descriptions[param.name])
                except:
                    return descs
        return descs

    def checkBeforeOpeningParametersDialog(self):
        msg = RUtils.checkRIsInstalled()
        if msg is not None:
            html = self.tr(
                '<p>This algorithm requires R to be run. Unfortunately it '
                'seems that R is not installed in your system or it is not '
                'correctly configured to be used from QGIS</p>'
                '<p><a href="http://docs.qgis.org/testing/en/docs/user_manual/processing/3rdParty.html">Click here</a> '
                'to know more about how to install and configure R to be used with QGIS</p>')
            return html

    def tr(self, string, context=''):
        if context == '':
            context = 'RAlgorithmProvider'
        return QCoreApplication.translate(context, string)

