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

import json
import os
from pathlib import Path

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsExpression,
    QgsExpressionContext,
    QgsGeometry,
    QgsPointXY,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingOutputDefinition,
    QgsProcessingParameterBand,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterCrs,
    QgsProcessingParameterEnum,
    QgsProcessingParameterExpression,
    QgsProcessingParameterExtent,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterNumber,
    QgsProcessingParameterPoint,
    QgsProcessingParameterRange,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterString,
    QgsProcessingParameterVectorDestination,
    QgsProcessingParameterVectorLayer,
    QgsProcessingUtils,
    QgsProviderRegistry,
    QgsVectorFileWriter,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication, QDate, QDateTime, QDir, QTime, QUrl
from qgis.PyQt.QtGui import QColor

from processing_r.gui.gui_utils import GuiUtils
from processing_r.processing.outputs import create_output_from_string
from processing_r.processing.parameters import create_parameter_from_string
from processing_r.processing.r_templates import RTemplates
from processing_r.processing.utils import RUtils

if Qgis.QGIS_VERSION_INT >= 31000:
    from qgis.core import QgsProcessingParameterColor  # pylint: disable=ungrouped-imports
if Qgis.QGIS_VERSION_INT >= 31400:
    from qgis.core import QgsProcessingParameterDateTime  # pylint: disable=ungrouped-imports


class RAlgorithm(QgsProcessingAlgorithm):  # pylint: disable=too-many-public-methods
    """
    R Script Algorithm
    """

    R_CONSOLE_OUTPUT = "R_CONSOLE_OUTPUT"
    RPLOTS = "RPLOTS"

    def __init__(self, description_file, script=None):
        super().__init__()

        self.r_templates = RTemplates()
        self.script = script
        self._name = ""
        self._display_name = ""
        self._group = ""
        self.description_file = os.path.realpath(description_file) if description_file else None
        self.error = None
        self.commands = []
        self.is_user_script = False
        if description_file:
            self.is_user_script = not description_file.startswith(RUtils.builtin_scripts_folder())

        self.show_plots = False
        self.pass_file_names = False
        self.show_console_output = False
        self.save_output_values = False
        self.plots_filename = ""
        self.output_values_filename = ""
        self.results = {}
        self.descriptions = None
        self.inline_help = None
        if self.script is not None:
            self.load_from_string()
        if self.description_file is not None:
            self.load_from_file()

        self.alg_context = QgsExpressionContext()

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

    def add_error_message(self, message):
        """
        Add error message to algorithme errors
        """
        if not self.error:
            self.error = message
        else:
            self.error += "\n"
            self.error += message

    def load_from_string(self):
        """
        Load the algorithm from a string
        """
        lines = self.script.split("\n")
        self._name = "unnamedalgorithm"
        self._display_name = self.tr("[Unnamed algorithm]")
        self.parse_script(iter(lines))

    def load_from_file(self):
        """
        Load the algorithm from a file
        """
        filename = os.path.basename(self.description_file)
        self._display_name = self._name
        self._name = filename[: filename.rfind(".")]
        self._display_name = self._name.replace("_", " ")

        help_file = self.description_file + ".help"
        if os.path.exists(help_file):
            with open(help_file, encoding="utf8") as f:
                self.descriptions = json.load(f)

        with open(self.description_file, "r", encoding="utf8") as f:
            lines = [line.strip() for line in f]
            # ordering for inline_help uses

        lines_help = []
        lines_header = []
        lines_r = []

        for line in lines:
            line = line.strip()
            if line.startswith("#'"):
                lines_help.append(line)
            elif line.startswith("##"):
                lines_header.append(line)
            else:
                lines_r.append(line)

        lines = lines_help + lines_header + lines_r

        self.parse_script(iter(lines))

    def parse_script(self, lines):
        """
        Parse the lines from an R script, initializing parameters and outputs as encountered
        """
        self.script = ""
        self.commands = []
        self.error = None
        self.show_plots = False
        self.show_console_output = False
        self.pass_file_names = False
        ender = 0
        line = next(lines).strip("\n").strip("\r")
        while ender < 10:
            if line.startswith("##"):
                try:
                    self.process_metadata_line(line)
                except Exception as e:  # pylint: disable=broad-except
                    self.add_error_message(
                        self.tr("This script has a syntax error.\n" "Exception {1} with line: {0}").format(line, e)
                    )
            elif line.startswith("#'"):
                try:
                    self.process_help_line(line)
                except Exception as e:  # pylint: disable=broad-except
                    self.add_error_message(
                        self.tr("This script has a syntax error.\n" "Exception {1} with help line: {0}...").format(
                            line[0:50], e
                        )
                    )
            elif line.startswith(">"):
                self.commands.append(line[1:])
                if not self.show_console_output:
                    self.addParameter(
                        QgsProcessingParameterFileDestination(
                            RAlgorithm.R_CONSOLE_OUTPUT,
                            self.tr("R Console Output"),
                            self.tr("HTML files (*.html)"),
                            optional=True,
                        )
                    )
                self.show_console_output = True
            else:
                if line == "":
                    ender += 1
                else:
                    ender = 0
                self.commands.append(line)
            self.script += line + "\n"
            try:
                line = next(lines).strip("\n").strip("\r")
            except StopIteration:
                break

    def process_metadata_line(self, line):  # pylint: disable=too-many-return-statements
        """
        Processes a "metadata" (##) line
        """
        line = line.replace("#", "")

        # special commands
        # showplots is the older version, should be considere obsolete
        if line.lower().strip().startswith("output_plots_to_html") or line.lower().strip().startswith("showplots"):
            self.show_plots = True
            self.addParameter(
                QgsProcessingParameterFileDestination(
                    RAlgorithm.RPLOTS, self.tr("R Plots"), self.tr("HTML files (*.html)"), optional=True
                )
            )
            return

        # these metadata commands are no longer supported
        if (
            line.lower().strip().startswith("load_raster_using_rgdal")
            or line.lower().strip().startswith("dontuserasterpackage")
            or line.lower().strip().startswith("load_vector_using_rgdal")
        ):
            raise QgsProcessingException("This command is no longer supported, `rgdal` package was removed from CRAN.")

        # passfilenames is the older version, should be considere obsolete
        if line.lower().strip().startswith("pass_filenames") or line.lower().strip().startswith("passfilenames"):
            self.pass_file_names = True
            return

        if line.lower().strip().startswith("dont_load_any_packages"):
            self.r_templates.auto_load_packages = False
            return

        value, type_ = self.split_tokens(line)
        if type_.lower().strip() == "group":
            self._group = value
            return
        if type_.lower().strip() == "name":
            self._name = self._display_name = value
            self._name = RUtils.strip_special_characters(self._name.lower())
            return
        if type_.lower().strip() == "display_name":
            self._display_name = value
            return
        if type_.lower().strip() == "github_install":
            self.r_templates.install_github = True
            self.r_templates.github_dependencies = value
            return

        # process enum with values and preparing its template
        if "enum literal" in RUtils.upgrade_parameter_line(line):
            self.r_templates.add_literal_enum(value)

        if "=expression" in line:
            self.r_templates.expressions.append(line)
            return

        self.process_parameter_line(line)

    def process_help_line(self, line):  # pylint: disable=too-many-return-statements
        """
        Processes a "help" (#') line
        """
        line = line.replace("#'", "")
        key, value = line.split(":", 1)
        if self.inline_help is None:
            help_dict = {}
        else:
            help_dict = self.inline_help
        if key.strip() == "":
            key = list(help_dict.keys())[-1]
            last_val = help_dict.get(key)
            value = last_val + " " + value.strip()
        help_dict[key.strip()] = value.strip()
        self.inline_help = help_dict

    @staticmethod
    def split_tokens(line):
        """
        Attempts to split a line into tokens
        """
        if "|" in line and line.startswith("QgsProcessing"):
            tokens = line.split("|")
            return tokens[1], line

        tokens = line.split("=")
        return tokens[0], tokens[1]

    def process_parameter_line(self, line):
        """
        Processes a single script line representing a parameter
        """
        value, _ = self.split_tokens(line)
        description = RUtils.create_descriptive_name(value)

        if not RUtils.is_valid_r_variable(value):
            self.add_error_message(
                self.tr(
                    "This script has a syntax error in variable name.\n"
                    '"{1}" is not a valid variable name in R.'
                    "Problem with line: {0}"
                ).format(line, value)
            )

        output = create_output_from_string(line)
        if output is not None:
            output.setName(value)
            output.setDescription(description)
            if issubclass(output.__class__, QgsProcessingOutputDefinition):
                self.addOutput(output)
                self.save_output_values = True
            else:
                # destination type parameter
                self.addParameter(output)
        else:
            param = create_parameter_from_string(line)

            if param is not None:
                # set help parameter
                if Qgis.QGIS_VERSION_INT >= 31600:
                    if self.descriptions is not None:
                        param.setHelp(self.descriptions.get(param.name()))
                    elif self.inline_help is not None:
                        param.setHelp(self.inline_help.get(param.name()))

                self.addParameter(param)
            else:
                self.add_error_message(
                    self.tr("This script has a syntax error.\n" "Problem with line: {0}").format(line)
                )

    def canExecute(self):
        """
        Returns True if the algorithm can be executed
        """
        if self.error:
            return False, self.error

        msg = RUtils.check_r_is_installed()
        if msg is not None:
            return False, msg

        return True, ""

    def processAlgorithm(self, parameters, context: QgsProcessingContext, feedback):
        """
        Executes the algorithm
        """
        self.results = {}

        self.alg_context = self.createExpressionContext(parameters, context)

        if RUtils.is_windows():
            path = RUtils.r_binary_folder()
            if path == "":
                raise QgsProcessingException(
                    self.tr("R folder is not configured.\nPlease configure it " "before running R scripts.")
                )

        feedback.pushInfo(self.tr("R execution commands"))

        output = RUtils.execute_r_algorithm(self, parameters, context, feedback)

        if self.show_plots:
            html_filename = self.parameterAsFileOutput(parameters, RAlgorithm.RPLOTS, context)
            if html_filename:
                with open(html_filename, "w", encoding="utf8") as f:
                    f.write('<html><img src="{}"/></html>'.format(QUrl.fromLocalFile(self.plots_filename).toString()))
                self.results[RAlgorithm.RPLOTS] = html_filename
        if self.show_console_output:
            html_filename = self.parameterAsFileOutput(parameters, RAlgorithm.R_CONSOLE_OUTPUT, context)
            if html_filename:
                with open(html_filename, "w", encoding="utf8") as f:
                    f.write(RUtils.html_formatted_console_output(output))
                self.results[RAlgorithm.R_CONSOLE_OUTPUT] = html_filename

        if self.save_output_values and self.output_values_filename:
            with open(self.output_values_filename, "r", encoding="utf8") as f:
                lines = [line.strip() for line in f]
            # get output values stored into the file
            outputs = self.parse_output_values(iter(lines))
            # merge output values into results
            for k, v in outputs.items():
                if k not in self.results:
                    self.results[k] = v

        return self.results

    def parse_output_values(self, lines):
        """
        Parse the lines from an output values file and returns a dict of output values

        The lines are:
        ##output1_name
        output1_value
        ##output2_name
        output2_value
        """
        outputs = {}
        if not self.save_output_values:
            return outputs

        output = None
        ender = 0
        line = next(lines).strip("\n").strip("\r")
        while ender < 10:
            if line.startswith("##"):
                name = line.replace("#", "")
                output = self.outputDefinition(name)
            else:
                if line == "":
                    ender += 1
                else:
                    ender = 0
                if not output:
                    continue
                if output.name() in outputs:
                    outputs[output.name()] += "\n\r" + line
                else:
                    outputs[output.name()] = line
            try:
                line = next(lines).strip("\n").strip("\r")
            except StopIteration:
                break

        return outputs

    def build_r_script(self, parameters, context, feedback):
        """
        Builds up the set of R commands to run for the script
        """
        commands = []
        commands += self.build_script_header_commands(parameters, context, feedback)
        commands += self.build_expressions(parameters, context, feedback)
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
                dest = dest.replace("\\", "/")
                commands.append(self.r_templates.write_raster_output(out.name(), dest))
                self.results[out.name()] = dest
            elif isinstance(out, QgsProcessingParameterVectorDestination):
                dest = self.parameterAsOutputLayer(parameters, out.name(), context)
                dest = dest.replace("\\", "/")
                filename = os.path.basename(dest)
                filename, ext = os.path.splitext(filename)
                if ext.lower() == ".csv":
                    # CSV table export
                    commands.append(self.r_templates.write_csv_output(out.name(), dest))
                else:
                    commands.append(self.r_templates.write_vector_output(out.name(), dest, filename))
                self.results[out.name()] = dest

        if self.save_output_values:
            for out in self.outputDefinitions():
                name = out.name()
                # write values only if output is not already in results
                if name in (self.R_CONSOLE_OUTPUT, self.RPLOTS):
                    continue
                if name in self.results:
                    continue
                # create file path for output values only if it is necessary
                if not self.output_values_filename:
                    self.output_values_filename = QgsProcessingUtils.generateTempFilename("processing_values.txt")
                # write output name and value with cat
                commands.extend(self.r_templates.write_cat_output(name, self.output_values_filename))

        if self.show_plots:
            commands.append(self.r_templates.dev_off())

        return commands

    def load_vector_layer_from_parameter(self, name, parameters, context, feedback):
        """
        Creates a dedicated command to load a vector into the workspace.
        :param name: name of the parameter
        :param parameters: Parameters of the algorithm.
        :param context: Processing context
        """
        if Qgis.QGIS_VERSION_INT >= 30900 and hasattr(self, "parameterAsCompatibleSourceLayerPathAndLayerName"):
            # requires qgis 3.10 or later!
            ogr_data_path, layer_name = self.parameterAsCompatibleSourceLayerPathAndLayerName(
                parameters,
                name,
                context,
                QgsVectorFileWriter.supportedFormatExtensions(),
                feedback=feedback,
                preferredFormat="gpkg",
            )
            if layer_name:
                return self.r_templates.set_variable_vector(name, QDir.fromNativeSeparators(ogr_data_path), layer_name)

            return self.r_templates.set_variable_vector(name, QDir.fromNativeSeparators(ogr_data_path))

        ogr_data_path = self.parameterAsCompatibleSourceLayerPath(
            parameters,
            name,
            context,
            QgsVectorFileWriter.supportedFormatExtensions(),
            feedback=feedback,
            preferredFormat="gpkg",
        )
        ogr_layer = QgsVectorLayer(ogr_data_path, "", "ogr")
        return self.load_vector_layer_command(name, ogr_layer, feedback)

    def build_vector_layer_import_command(self, variable_name, layer, context, feedback):
        """
        Returns an import command for the specified vector layer, storing it in a variable
        """
        if layer is None:
            return self.r_templates.set_variable_null(variable_name)

        is_ogr_disk_based_layer = layer is not None and layer.dataProvider().name() == "ogr"
        if is_ogr_disk_based_layer:
            # we only support direct reading of disk based ogr layers -- not ogr postgres layers, etc
            source_parts = QgsProviderRegistry.instance().decodeUri("ogr", layer.source())
            if not source_parts.get("path"):
                is_ogr_disk_based_layer = False
            elif source_parts.get("layerId"):
                # no support for directly reading layers by id in R
                is_ogr_disk_based_layer = False

        if not is_ogr_disk_based_layer:
            # parameter is not a vector layer or not an OGR layer - try to convert to a source compatible with
            # R OGR inputs and extract selection if required
            path = QgsProcessingUtils.convertToCompatibleFormat(
                layer,
                False,
                variable_name,
                compatibleFormats=QgsVectorFileWriter.supportedFormatExtensions(),
                preferredFormat="gpkg",
                context=context,
                feedback=feedback,
            )
            ogr_layer = QgsVectorLayer(path, "", "ogr")
            return self.load_vector_layer_command(variable_name, ogr_layer, None)

        # already an ogr disk based layer source
        return self.load_vector_layer_command(variable_name, layer, None)

    def load_vector_layer_command(self, name, layer, _):
        """
        Creates a command to load a vector layer into the workspace
        """
        source_parts = QgsProviderRegistry.instance().decodeUri("ogr", layer.source())
        file_path = source_parts.get("path")
        if self.pass_file_names:
            return self.r_templates.set_variable_string(name, QDir.fromNativeSeparators(file_path))

        layer_name = source_parts.get("layerName")
        if layer_name:
            return self.r_templates.set_variable_vector(name, QDir.fromNativeSeparators(file_path), layer=layer_name)

        # no layer name -- readOGR expects the folder, with the filename as layer
        return self.r_templates.set_variable_vector(name, QDir.fromNativeSeparators(file_path))

    def build_script_header_commands(self, _, __, ___):
        """
        Builds the set of script startup commands for the algorithm
        """
        return self.r_templates.build_script_header_commands(self.script)

    def build_raster_layer_import_command(self, variable_name, layer):
        """
        Returns an import command for the specified raster layer, storing it in a variable
        """
        if layer is None:
            return self.r_templates.set_variable_null(variable_name)

        if layer.dataProvider().name() != "gdal":
            raise QgsProcessingException(
                self.tr("Layer {} is not a GDAL layer. Currently only GDAL based raster layers are supported.").format(
                    variable_name
                )
            )

        path = QgsProviderRegistry.instance().decodeUri(layer.dataProvider().name(), layer.source())["path"]
        value = QDir.fromNativeSeparators(path)
        if self.pass_file_names:
            return self.r_templates.set_variable_string(variable_name, value)

        return self.r_templates.set_variable_raster(variable_name, value)

    def build_expressions(self, parameters, context, feedback):  # pylint: disable=unused-argument
        """
        Builds set of R input data commands based on QGIS Expression variables.
        """
        commands = []

        for line in self.r_templates.expressions:
            param = create_parameter_from_string(line)

            if isinstance(param, QgsProcessingParameterExpression):
                exp = QgsExpression(param.defaultValue())

                if not exp.prepare(self.alg_context):
                    raise QgsProcessingException(
                        self.tr(
                            "Expression with name `{0}` and value `{1}` is malformed. "
                            "Error: {2}.".format(param.name(), param.defaultValue(), exp.parserErrorString())
                        )
                    )

                exp_result = exp.evaluate(self.alg_context)

                if exp.hasEvalError():
                    raise QgsProcessingException(
                        self.tr(
                            "Expression with name `{0}` and value `{1}` can not be evaluated. " "Error: {2}."
                        ).format(param.name(), param.defaultValue(), exp.evalErrorString())
                    )

                commands.append(self.expression_as_r_command(param, exp_result))

        return commands

    def build_import_commands(
        self, parameters, context, feedback  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    ):
        """
        Builds the set of input commands for the algorithm
        """
        commands = []

        for param in self.parameterDefinitions():
            if param.isDestination():
                continue

            if param.name() not in parameters or parameters[param.name()] is None:
                commands.append(self.r_templates.set_variable_null(param.name()))
                continue

            if isinstance(param, QgsProcessingParameterRasterLayer):
                rl = self.parameterAsRasterLayer(parameters, param.name(), context)
                commands.append(self.build_raster_layer_import_command(param.name(), rl))
            elif isinstance(param, QgsProcessingParameterBand):
                value = self.parameterAsInt(parameters, param.name(), context)
                commands.append(self.r_templates.set_variable_directly(param.name(), value))
            elif isinstance(param, QgsProcessingParameterVectorLayer):
                commands.append(self.load_vector_layer_from_parameter(param.name(), parameters, context, feedback))
            elif isinstance(param, QgsProcessingParameterFeatureSource):
                commands.append(self.load_vector_layer_from_parameter(param.name(), parameters, context, feedback))
            elif isinstance(param, QgsProcessingParameterExtent):
                extent = self.parameterAsExtent(parameters, param.name(), context)
                # Extent from raster package is "xmin, xmax, ymin, ymax" like in Processing
                # http://www.inside-r.org/packages/cran/raster/docs/Extent
                commands.append(
                    self.r_templates.set_variable_extent(
                        param.name(), extent.xMinimum(), extent.xMaximum(), extent.yMinimum(), extent.yMaximum()
                    )
                )
            elif isinstance(param, QgsProcessingParameterCrs):
                crs = self.parameterAsCrs(parameters, param.name(), context)
                if crs.isValid():
                    if crs.authid().lower().startswith("user:") or crs.authid() == "":
                        commands.append(
                            self.r_templates.set_variable_string(
                                param.name(), crs.toWkt(QgsCoordinateReferenceSystem.WKT2_2019_SIMPLIFIED)
                            )
                        )
                    else:
                        commands.append(self.r_templates.set_variable_string(param.name(), crs.authid()))
                else:
                    commands.append(self.r_templates.set_variable_null(param.name()))
            elif isinstance(param, QgsProcessingParameterFile):
                value = self.parameterAsString(parameters, param.name(), context)
                commands.append(self.r_templates.set_variable_string(param.name(), QDir.fromNativeSeparators(value)))
            elif isinstance(param, QgsProcessingParameterString):
                value = self.parameterAsString(parameters, param.name(), context)
                commands.append(self.r_templates.set_variable_string(param.name(), value))
            elif isinstance(param, QgsProcessingParameterField):
                if param.allowMultiple():
                    value = self.parameterAsFields(parameters, param.name(), context)
                    commands.append(self.r_templates.set_variable_string_list(param.name(), value))
                else:
                    value = self.parameterAsString(parameters, param.name(), context)
                    commands.append(self.r_templates.set_variable_string(param.name(), value))
            elif isinstance(param, QgsProcessingParameterNumber):
                value = self.parameterAsDouble(parameters, param.name(), context)
                commands.append(self.r_templates.set_variable_directly(param.name(), value))
            elif isinstance(param, QgsProcessingParameterEnum):
                commands.append(self.process_enum(parameters, param, context))
            elif isinstance(param, QgsProcessingParameterBoolean):
                value = self.parameterAsBool(parameters, param.name(), context)
                value = "TRUE" if value else "FALSE"
                commands.append(self.r_templates.set_variable_directly(param.name(), value))
            elif isinstance(param, QgsProcessingParameterPoint):
                point: QgsPointXY = self.parameterAsPoint(parameters, param.name(), context)
                crs: QgsCoordinateReferenceSystem = self.parameterAsPointCrs(parameters, param.name(), context)
                commands.extend(self.r_templates.set_point(param.name(), point, crs))
            elif isinstance(param, QgsProcessingParameterRange):
                rgn: list = self.parameterAsRange(parameters, param.name(), context)
                commands.extend(self.r_templates.set_range(param.name(), rgn))
            elif isinstance(param, QgsProcessingParameterMultipleLayers):
                layer_idx = 0
                layers = self.parameterAsLayerList(parameters, param.name(), context)
                if param.layerType() == QgsProcessing.TypeRaster:
                    for layer in layers:
                        variable_name = "tempvar{}".format(layer_idx)
                        commands.append(self.build_raster_layer_import_command(variable_name, layer))
                        layer_idx += 1
                else:
                    for layer in layers:
                        variable_name = "tempvar{}".format(layer_idx)
                        commands.append(self.build_vector_layer_import_command(variable_name, layer, context, feedback))
                        layer_idx += 1

                s = ""
                s += param.name()
                s += " = list("
                layer_idx = 0
                for _ in layers:
                    if layer_idx != 0:
                        s += ","
                    s += "tempvar{}".format(layer_idx)
                    layer_idx += 1
                s += ")"
                commands.append(s)

            if Qgis.QGIS_VERSION_INT >= 31000:
                if isinstance(param, QgsProcessingParameterColor):
                    color: QColor = self.parameterAsColor(parameters, param.name(), context)
                    commands.extend(self.r_templates.set_color(param.name(), color))

            if Qgis.QGIS_VERSION_INT >= 31400:
                if isinstance(param, QgsProcessingParameterDateTime):
                    datetime: QDateTime = self.parameterAsDateTime(parameters, param.name(), context)
                    commands.extend(self.r_templates.set_datetime(param.name(), datetime))

        # folder, file/html output paths
        for param in self.destinationParameterDefinitions():
            if isinstance(param, QgsProcessingParameterFolderDestination):
                folder = self.parameterAsString(parameters, param.name(), context)
                Path(folder).mkdir(parents=True, exist_ok=True)
                commands.append(self.r_templates.set_variable_string(param.name(), QDir.fromNativeSeparators(folder)))
                self.save_output_values = True
            elif isinstance(param, QgsProcessingParameterFileDestination):
                filename = self.parameterAsFileOutput(parameters, param.name(), context)
                Path(filename).parent.mkdir(parents=True, exist_ok=True)
                commands.append(self.r_templates.set_variable_string(param.name(), QDir.fromNativeSeparators(filename)))
                self.save_output_values = True

        if self.show_plots:
            html_filename = self.parameterAsFileOutput(parameters, RAlgorithm.RPLOTS, context)
            path, _ = os.path.splitext(html_filename)
            self.plots_filename = path + ".png"
            self.plots_filename = self.plots_filename.replace("\\", "/")
            commands.append(self.r_templates.create_png(self.plots_filename))

        return commands

    def expression_as_r_command(self, parameter, expression):  # pylint: disable=too-many-return-statements
        """
        Returns input parameter as R code based on type of parameter.
        """
        parameter_name = parameter.name()

        if isinstance(expression, str):
            return self.r_templates.set_variable_string(parameter_name, expression)

        if isinstance(expression, (int, float)):
            return self.r_templates.set_variable_directly(parameter_name, expression)

        if isinstance(expression, QDateTime):
            return self.r_templates.set_datetime(parameter_name, expression)

        if isinstance(expression, QDate):
            return self.r_templates.set_date(parameter_name, expression)

        if isinstance(expression, QTime):
            return self.r_templates.set_time(parameter_name, expression)

        if isinstance(expression, QgsGeometry):
            return self.r_templates.set_variable_geom(parameter_name, expression.asWkt())

        if isinstance(expression, list):
            return self.r_templates.set_variable_list(parameter_name, expression)

        return ""

    def build_r_commands(self, _, __, ___):
        """
        Returns the body of the R script
        """
        return self.commands

    def shortHelpString(self):
        """
        Returns the algorithms helper string
        """
        if self.descriptions is not None:
            return QgsProcessingUtils.formatHelpMapAsHtml(self.descriptions, self)

        if self.inline_help is not None:
            return QgsProcessingUtils.formatHelpMapAsHtml(self.inline_help, self)

        return ""

    def tr(self, string, context=""):
        """
        Translates a string
        """
        if context == "":
            context = "RAlgorithmProvider"
        return QCoreApplication.translate(context, string)

    def process_enum(self, parameters, param, context) -> str:
        """
        Returns string representation of enum `param`.
        """

        enum_code = ""

        if self.r_templates.is_literal_enum(param.name()):
            if param.allowMultiple():
                values = self.parameterAsEnums(parameters, param.name(), context)
                enum_values = self.parameterDefinition(param.name()).options()
                enum_values = [enum_values[i] for i in values]

                enum_code = self.r_templates.set_variable_string_list(param.name(), enum_values)

            else:
                value = self.parameterAsEnum(parameters, param.name(), context)
                enum_value = self.parameterDefinition(param.name()).options()
                enum_code = self.r_templates.set_variable_enum_value(param.name(), value, enum_value)

        else:
            if param.allowMultiple():
                values = self.parameterAsEnums(parameters, param.name(), context)
                value = f'c({", ".join([str(i) for i in values])})'
                enum_code = self.r_templates.set_variable_directly(param.name(), value)

            else:
                value = self.parameterAsEnum(parameters, param.name(), context)
                enum_code = self.r_templates.set_variable_directly(param.name(), value)

        return enum_code
