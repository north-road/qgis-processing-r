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

import os
import json

from qgis.core import (QgsProcessing,
                       QgsProviderRegistry,
                       QgsProcessingAlgorithm,
                       QgsProcessingException,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterField,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingOutputDefinition,
                       QgsVectorFileWriter,
                       QgsVectorLayer,
                       QgsProcessingUtils)
from qgis.PyQt.QtCore import QCoreApplication
from processing.core.parameters import getParameterFromString
from r.processing.outputs import create_output_from_string
from r.processing.utils import RUtils
from r.gui.gui_utils import GuiUtils


class RAlgorithm(QgsProcessingAlgorithm):  # pylint: disable=too-many-public-methods
    """
    R Script Algorithm
    """

    R_CONSOLE_OUTPUT = 'R_CONSOLE_OUTPUT'
    RPLOTS = 'RPLOTS'

    def __init__(self, description_file, script=None):
        super().__init__()

        self.script = script
        self._name = ''
        self._display_name = ''
        self._group = ''
        self.description_file = os.path.realpath(description_file) if description_file else ''
        self.error = None
        self.commands = list()
        self.is_user_script = False
        if description_file:
            self.is_user_script = not description_file.startswith(RUtils.builtin_scripts_folder())

        self.show_plots = False
        self.use_raster_package = False
        self.pass_file_names = False
        self.show_console_output = False
        self.plots_filename = ''
        self.results = {}
        if self.script is not None:
            self.load_from_string()
        if self.description_file is not None:
            self.load_from_file()

    def createInstance(self):
        """
        Returns a new instance of this algorithm
        """
        if self.description_file is not None:
            return RAlgorithm(self.description_file)

        return RAlgorithm(description_file=None, script=self.script)

    def initAlgorithm(self, _=None):
        """
        Initializes the algorithm
        """
        pass  # pylint: disable=unnecessary-pass

    def icon(self):
        """
        Returns the algorithm's icon
        """
        return GuiUtils.get_icon("providerR.svg")

    def svgIconPath(self):
        """
        Returns a path to the algorithm's icon as a SVG file
        """
        return GuiUtils.get_icon_svg("providerR.svg")

    def name(self):
        """
        Internal unique id for algorithm
        """
        return self._name

    def displayName(self):
        """
        User friendly display name
        """
        return self._display_name

    def shortDescription(self):
        """
        Returns the path to the script file, for use in toolbox tooltips
        """
        return self.description_file

    def group(self):
        """
        Returns the algorithm's group
        """
        return self._group

    def groupId(self):
        """
        Returns the algorithm's group ID
        """
        return self._group

    def load_from_string(self):
        """
        Load the algorithm from a string
        """
        lines = self.script.split('\n')
        self._name = 'unnamedalgorithm'
        self._display_name = self.tr('[Unnamed algorithm]')
        self.parse_script(iter(lines))

    def load_from_file(self):
        """
        Load the algorithm from a file
        """
        filename = os.path.basename(self.description_file)
        self._display_name = self._name
        self._name = filename[:filename.rfind('.')]
        self._display_name = self._name.replace('_', ' ')
        with open(self.description_file, 'r') as f:
            lines = [line.strip() for line in f]
        self.parse_script(iter(lines))

    def parse_script(self, lines):
        """
        Parse the lines from an R script, initializing parameters and outputs as encountered
        """
        self.script = ''
        self.commands = list()
        self.error = None
        self.show_plots = False
        self.show_console_output = False
        self.use_raster_package = True
        self.pass_file_names = False
        ender = 0
        line = next(lines).strip('\n').strip('\r')
        while ender < 10:
            if line.startswith('##'):
                try:
                    self.process_metadata_line(line)
                except Exception:  # pylint: disable=broad-except
                    self.error = self.tr('This script has a syntax error.\n'
                                         'Problem with line: {0}').format(line)
            elif line.startswith('>'):
                self.commands.append(line[1:])
                if not self.show_console_output:
                    self.addParameter(
                        QgsProcessingParameterFileDestination(RAlgorithm.R_CONSOLE_OUTPUT, self.tr('R Console Output'),
                                                              self.tr('HTML files (*.html)'), optional=True))
                self.show_console_output = True
            else:
                if line == '':
                    ender += 1
                else:
                    ender = 0
                self.commands.append(line)
            self.script += line + '\n'
            try:
                line = next(lines).strip('\n').strip('\r')
            except StopIteration:
                break

    def process_metadata_line(self, line):
        """
        Processes a "metadata" (##) line
        """
        line = line.replace('#', '')

        # special commands
        if line.lower().strip().startswith('showplots'):
            self.show_plots = True
            self.addParameter(QgsProcessingParameterFileDestination(RAlgorithm.RPLOTS, self.tr('R Plots'),
                                                                    self.tr('HTML files (*.html)'), optional=True))
            return
        if line.lower().strip().startswith('dontuserasterpackage'):
            self.use_raster_package = False
            return
        if line.lower().strip().startswith('passfilenames'):
            self.pass_file_names = True
            return

        value, type_ = self.split_tokens(line)
        if type_.lower().strip() == 'group':
            self._group = value
            return
        if type_.lower().strip() == 'name':
            self._name = self._display_name = value
            self._name = RUtils.strip_special_characters(self._name.lower())
            return

        self.process_parameter_line(line)

    @staticmethod
    def split_tokens(line):
        """
        Attempts to split a line into tokens
        """
        tokens = line.split('=')
        return tokens[0], tokens[1]

    def process_parameter_line(self, line):
        """
        Processes a single script line representing a parameter
        """
        value, _ = self.split_tokens(line)
        description = RUtils.create_descriptive_name(value)

        output = create_output_from_string(line)
        if output is not None:
            output.setName(value)
            output.setDescription(description)
            if issubclass(output.__class__, QgsProcessingOutputDefinition):
                self.addOutput(output)
            else:
                # destination type parameter
                self.addParameter(output)
        else:
            line = RUtils.upgrade_parameter_line(line)
            param = getParameterFromString(line)
            if param is not None:
                self.addParameter(param)
            else:
                self.error = self.tr('This script has a syntax error.\n'
                                     'Problem with line: {0}').format(line)

    def canExecute(self):
        """
        Returns True if the algorithm can be executed
        """
        if self.error:
            return False, self.error

        msg = RUtils.check_r_is_installed()
        if msg is not None:
            return False, msg

        return True, ''

    def processAlgorithm(self, parameters, context, feedback):
        """
        Executes the algorithm
        """
        self.results = {}

        if RUtils.is_windows():
            path = RUtils.r_binary_folder()
            if path == '':
                raise QgsProcessingException(
                    self.tr('R folder is not configured.\nPlease configure it '
                            'before running R scripts.'))

        feedback.pushInfo(self.tr('R execution commands'))
        script_lines = self.build_r_script(parameters, context, feedback)
        for line in script_lines:
            feedback.pushCommandInfo(line)

        output = RUtils.execute_r_algorithm(self, parameters, context, feedback)

        if self.show_plots:
            html_filename = self.parameterAsFileOutput(parameters, RAlgorithm.RPLOTS, context)
            if html_filename:
                with open(html_filename, 'w') as f:
                    f.write('<html><img src="' + self.plots_filename + '"/></html>')
                self.results[RAlgorithm.RPLOTS] = html_filename
        if self.show_console_output:
            html_filename = self.parameterAsFileOutput(parameters, RAlgorithm.R_CONSOLE_OUTPUT, context)
            if html_filename:
                with open(html_filename, 'w') as f:
                    f.write(RUtils.html_formatted_console_output(output))
                self.results[RAlgorithm.R_CONSOLE_OUTPUT] = html_filename

        return self.results

    def build_r_script(self, parameters, context, feedback):
        """
        Builds up the set of R commands to run for the script
        """
        commands = []
        commands += self.build_script_header_commands(parameters, context, feedback)
        commands += self.build_import_commands(parameters, context, feedback)
        commands += self.build_r_commands(parameters, context, feedback)
        commands += self.build_export_commands(parameters, context, feedback)

        return commands

    def build_export_commands(self, parameters, context, _):
        """
        Builds up the set of R commands for exporting results
        """
        commands = []
        for out in self.destinationParameterDefinitions():
            if isinstance(out, QgsProcessingParameterRasterDestination):
                dest = self.parameterAsOutputLayer(parameters, out.name(), context)
                dest = dest.replace('\\', '/')
                if self.use_raster_package or self.pass_file_names:
                    commands.append('writeRaster({},"{}", overwrite=TRUE)'.format(out.name(), dest))
                else:
                    if not dest.lower().endswith('tif'):
                        dest = dest + '.tif'
                    commands.append('writeGDAL({},"{}")'.format(out.name(), dest))
                self.results[out.name()] = dest
            elif isinstance(out, QgsProcessingParameterVectorDestination):
                dest = self.parameterAsOutputLayer(parameters, out.name(), context)
                dest = dest.replace('\\', '/')
                filename = os.path.basename(dest)
                filename, ext = os.path.splitext(filename)
                if ext.lower() == '.csv':
                    # CSV table export
                    commands.append('write.csv(' + out.name() + ',"' + dest + '")')
                else:
                    commands.append('writeOGR(' + out.name() + ',"' + dest + '","' +
                                    filename + '", driver="{}")'.format(QgsVectorFileWriter.driverForExtension(ext)))
                    self.results[out.name()] = dest

        if self.show_plots:
            commands.append('dev.off()')

        return commands

    def load_vector_layer_from_parameter(self, name, parameters, context, feedback):
        """
        Creates a dedicated command to load a vector into the workspace.
        :param name: name of the parameter
        :param parameters: Parameters of the algorithm.
        :param context: Processing context
        """
        layer = self.parameterAsVectorLayer(parameters, name, context)

        is_ogr_disk_based_layer = layer is not None and layer.dataProvider().name() == 'ogr'
        if is_ogr_disk_based_layer:
            # we only support direct reading of disk based ogr layers -- not ogr postgres layers, etc
            source_parts = QgsProviderRegistry.instance().decodeUri('ogr', layer.source())
            if not source_parts.get('path'):
                is_ogr_disk_based_layer = False
            elif source_parts.get('layerId'):
                # no support for directly reading layers by id in grass
                is_ogr_disk_based_layer = False

        if not is_ogr_disk_based_layer:
            # parameter is not a vector layer or not an OGR layer - try to convert to a source compatible with
            # grass OGR inputs and extract selection if required
            path = self.parameterAsCompatibleSourceLayerPath(parameters, name, context,
                                                             QgsVectorFileWriter.supportedFormatExtensions(),
                                                             feedback=feedback)
            ogr_layer = QgsVectorLayer(path, '', 'ogr')
            return self.load_vector_layer_command(name, ogr_layer, feedback)

        # already an ogr disk based layer source
        return self.load_vector_layer_command(name, layer, feedback)

    def load_vector_layer_command(self, name, layer, _):
        """
        Creates a command to load a vector layer into the workspace
        """
        source_parts = QgsProviderRegistry.instance().decodeUri('ogr', layer.source())
        file_path = source_parts.get('path')
        if self.pass_file_names:
            return '{}="{}"'.format(name, file_path)

        layer_name = source_parts.get('layerName')
        if layer_name:
            # eg geopackage source
            return '{}=readOGR("{}",layer="{}")'.format(name, file_path, layer_name)

        # no layer name -- readOGR expects the folder, with the filename as layer
        folder, file_name = os.path.split(file_path)
        base_name, _ = os.path.splitext(file_name)
        return '{}=readOGR("{}",layer="{}")'.format(name, folder, base_name)

    def build_script_header_commands(self, _, __, ___):
        """
        Builds the set of script startup commands for the algorithm
        """
        commands = list()

        # Just use main mirror
        commands.append('options("repos"="{}")'.format(RUtils.package_repo()))

        # Try to install packages if needed
        if RUtils.use_user_library():
            commands.append('.libPaths(\"' + str(RUtils.r_library_folder()).replace('\\', '/') + '\")')

        packages = RUtils.get_required_packages(self.script)
        packages.extend(['rgdal', 'raster'])
        for p in packages:
            commands.append('tryCatch(find.package("' + p +
                            '"), error=function(e) install.packages("' + p +
                            '", dependencies=TRUE))')
        commands.append('library("raster")')
        commands.append('library("rgdal")')

        return commands

    def build_import_commands(self,  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
                              parameters, context, feedback):
        """
        Builds the set of input commands for the algorithm
        """
        commands = list()

        for param in self.parameterDefinitions():
            if param.isDestination():
                continue

            if param.name() not in parameters or parameters[param.name()] is None:
                commands.append('{}=NULL'.format(param.name()))
                continue

            if isinstance(param, QgsProcessingParameterRasterLayer):
                rl = self.parameterAsRasterLayer(parameters, param.name(), context)
                if rl is None:
                    commands.append('{}=NULL'.format(param.name()))
                else:
                    if rl.dataProvider().name() != 'gdal':
                        raise QgsProcessingException(
                            self.tr(
                                "Layer {} is not a GDAL layer. Currently only GDAL based raster layers are supported."
                            ).format(param.name()))

                    path = QgsProviderRegistry.instance().decodeUri(rl.dataProvider().name(), rl.source())['path']
                    value = path.replace('\\', '/')
                    if self.pass_file_names:
                        commands.append(param.name() + ' = "' + value + '"')
                    elif self.use_raster_package:
                        commands.append(param.name() + ' = ' + 'brick("' + value + '")')
                    else:
                        commands.append(param.name() + ' = ' + 'readGDAL("' + value + '")')
            elif isinstance(param, QgsProcessingParameterVectorLayer):
                commands.append(self.load_vector_layer_from_parameter(param.name(), parameters, context, feedback))
            # elif isinstance(param, ParameterTable):
            #     if param.value is None:
            #         commands.append(param.name + '= NULL')
            #     else:
            #         value = param.value
            #         if not value.lower().endswith('csv'):
            #             raise GeoAlgorithmExecutionException(
            #                 'Unsupported input file format.\n' + value)
            #         if self.pass_file_names:
            #             commands.append(param.name + ' = "' + value + '"')
            #         else:
            #             commands.append(param.name + ' <- read.csv("' + value +
            #                             '", head=TRUE, sep=",")')
            elif isinstance(param, QgsProcessingParameterExtent):
                extent = self.parameterAsExtent(parameters, param.name(), context)
                # Extent from raster package is "xmin, xmax, ymin, ymax" like in Processing
                # http://www.inside-r.org/packages/cran/raster/docs/Extent
                commands.append('{}=extent({},{},{},{})'.format(param.name(),
                                                                extent.xMinimum(),
                                                                extent.xMaximum(),
                                                                extent.yMinimum(),
                                                                extent.yMaximum()))
            elif isinstance(param, QgsProcessingParameterCrs):
                crs = self.parameterAsCrs(parameters, param.name(), context)
                if crs.isValid():
                    commands.append('{}="{}"'.format(param.name(), crs.authid()))
                else:
                    commands.append('{}=NULL'.format(param.name()))
            elif isinstance(param,
                            (QgsProcessingParameterField, QgsProcessingParameterString, QgsProcessingParameterFile)):
                value = self.parameterAsString(parameters, param.name(), context)
                commands.append('{}="{}"'.format(param.name(), value))
            elif isinstance(param, QgsProcessingParameterNumber):
                value = self.parameterAsDouble(parameters, param.name(), context)
                commands.append('{}="{}"'.format(param.name(), value))
            elif isinstance(param, QgsProcessingParameterEnum):
                value = self.parameterAsEnum(parameters, param.name(), context)
                commands.append('{}={}'.format(param.name(), value))
            elif isinstance(param, QgsProcessingParameterBoolean):
                value = self.parameterAsBool(parameters, param.name(), context)
                commands.append('{}={}'.format(param.name(), 'TRUE' if value else 'FALSE'))
            elif isinstance(param, QgsProcessingParameterMultipleLayers):
                layer_idx = 0
                layers = []
                if param.layerType() == QgsProcessing.TypeRaster:
                    pass
                    # layers = param.value.split(';')
                    # for layer in layers:
                    #    layer = layer.replace('\\', '/')
                    #    if self.pass_file_names:
                    #        commands.append('tempvar' + str(layer_idx) + ' <- "' +
                    #                        layer + '"')
                    #    elif self.use_raster_package:
                    #        commands.append('tempvar' + str(layer_idx) + ' <- ' +
                    #                        'brick("' + layer + '")')
                    #    else:
                    #        commands.append('tempvar' + str(layer_idx) + ' <- ' +
                    #                        'readGDAL("' + layer + '")')
                    #    #layer_idx += 1
                else:
                    pass
                    # exported = param.getSafeExportedLayers()#
                    # layers = exported.split(';')
                    # for layer in layers:
                    #    if not layer.lower().endswith('shp') \
                    #            and not self.pass_file_names:
                    #        raise GeoAlgorithmExecutionException(
                    #            'Unsupported input file format.\n' + layer)
                    #    layer = layer.replace('\\', '/')
                    #    filename = os.path.basename(layer)
                    #    filename = filename[:-4]
                    #    if self.pass_file_names:
                    #        commands.append('tempvar' + str(layer_idx) + ' <- "' +
                    #                        layer + '"')
                    #    else:
                    #        commands.append('tempvar' + str(layer_idx) + ' <- ' +
                    #                        'readOGR("' + layer + '",layer="' +
                    #                        filename + '")')
                    #    layer_idx += 1
                s = ''
                s += param.name
                s += ' = c('
                layer_idx = 0
                for _ in layers:
                    if layer_idx != 0:
                        s += ','
                    s += 'tempvar{}'.format(layer_idx)
                    layer_idx += 1
                s += ')\n'
                commands.append(s)
            # TODO folder, file/html output paths should be set here

        if self.show_plots:
            html_filename = self.parameterAsFileOutput(parameters, RAlgorithm.RPLOTS, context)
            path, _ = os.path.splitext(html_filename)
            self.plots_filename = path + '.png'
            self.plots_filename = self.plots_filename.replace('\\', '/')
            commands.append('png("' + self.plots_filename + '")')

        return commands

    def build_r_commands(self, _, __, ___):
        """
        Returns the body of the R script
        """
        return self.commands

    def shortHelpString(self):
        """
        Returns the algorithms helper string
        """
        if self.description_file is None:
            return ''

        help_file = self.description_file + '.help'
        print(help_file)
        if os.path.exists(help_file):
            with open(help_file) as f:
                descriptions = json.load(f)

            return QgsProcessingUtils.formatHelpMapAsHtml(descriptions, self)

        return ''

    def tr(self, string, context=''):
        """
        Translates a string
        """
        if context == '':
            context = 'RAlgorithmProvider'
        return QCoreApplication.translate(context, string)
