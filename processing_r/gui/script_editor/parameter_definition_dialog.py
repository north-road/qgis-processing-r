# -*- coding: utf-8 -*-

"""
***************************************************************************
    ModelerParameterDefinitionDialog.py
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

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

import math

from qgis.PyQt.QtCore import (Qt,
                              QByteArray,
                              QCoreApplication)
from qgis.PyQt.QtWidgets import (QDialog,
                                 QVBoxLayout,
                                 QLabel,
                                 QLineEdit,
                                 QComboBox,
                                 QCheckBox,
                                 QDialogButtonBox,
                                 QMessageBox)

from qgis.gui import (QgsExpressionLineEdit,
                      QgsProjectionSelectionWidget,
                      QgsProcessingParameterDefinitionDialog,
                      QgsProcessingParameterWidgetContext)
from qgis.core import (QgsApplication,
                       QgsSettings,
                       QgsProcessing,
                       QgsProject,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterMapLayer,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterPoint,
                       QgsProcessingParameterMatrix,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterScale,
                       QgsProcessingParameterRange,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterExpression,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterBand,
                       QgsProcessingDestinationParameter,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingModelAlgorithm,
                       QgsProcessingContext,
                       QgsProcessingParameters,
                       QgsProcessingModelParameter)

from processing.gui.DestinationSelectionPanel import DestinationSelectionPanel
from processing.gui.enummodelerwidget import EnumModelerWidget
from processing.gui.matrixmodelerwidget import MatrixModelerWidget
from processing.core import parameters
from processing.modeler.exceptions import UndefinedParameterException
from processing.core.parameters import getParameterFromString

from qgis.utils import iface


# This class is ported from the QGIS core Processing modeler
# Unfortunately generalising the core editor to allow everything we want in an R editor
# isn't feasible... so lots of duplicate code here :(
# Try to keep the diff between the two as small as possible, to allow porting fixes from QGIS core

def create_fake_model(script_contents):
    # first extract all lines which look like parameter definitions
    lines = [l.strip()[2:] for l in script_contents.split('\n') if l.strip().startswith('##')]
    model = QgsProcessingModelAlgorithm()
    for line in lines:
        param = None
        try:
            param = getParameterFromString(line, context="")
        except TypeError:
            param = getParameterFromString(line)

        if param is not None:
            model.addModelParameter(param, QgsProcessingModelParameter(param.name()))
    return model


def create_new_parameter(parameter_type, script_contents=''):
    """
    Allows users to create a new parameter via the GUI configuration dialog, and returns this parameter
    """

    # we have to fake things a bit. The parameter definition dialog requires a model to work
    model = create_fake_model(script_contents)

    #    existing_param = self.model.parameterDefinition(self.element.parameterName())
    new_param = None
    if ModelerParameterDefinitionDialog.use_legacy_dialog(paramType=parameter_type):
        # boo, old api
        dlg = ModelerParameterDefinitionDialog(model,
                                               paramType=parameter_type)
        if dlg.exec_():
            new_param = dlg.param
    else:
        # yay, use new API!
        context = create_context()
        widget_context = create_widget_context(model)
        dlg = QgsProcessingParameterDefinitionDialog(type=parameter_type,
                                                     context=context,
                                                     widgetContext=widget_context,
                                                     algorithm=model)
        if dlg.exec_():
            new_param = dlg.createParameter()

            validChars = \
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            safeName = ''.join(c for c in new_param.description() if c in validChars)
            name = safeName.lower()
            i = 2
            while model.parameterDefinition(name):
                name = safeName.lower() + str(i)
                i += 1

            new_param.setName(name)

    return new_param


def create_context():
    context = QgsProcessingContext()
    context.setProject(QgsProject.instance())
    return context


def create_widget_context(model):
    """
    Returns a new widget context for use in the model editor
    """
    widget_context = QgsProcessingParameterWidgetContext()
    widget_context.setProject(QgsProject.instance())
    if iface is not None:
        widget_context.setMapCanvas(iface.mapCanvas())
    widget_context.setModel(model)
    return widget_context



class ModelerParameterDefinitionDialog(QDialog):

    @staticmethod
    def use_legacy_dialog(param=None, paramType=None):
        if paramType in (parameters.PARAMETER_TABLE_FIELD,
                         parameters.PARAMETER_BAND,
                         parameters.PARAMETER_VECTOR,
                         parameters.PARAMETER_TABLE,
                         parameters.PARAMETER_MULTIPLE,
                         parameters.PARAMETER_NUMBER,
                         parameters.PARAMETER_DISTANCE,
                         parameters.PARAMETER_SCALE,
                         parameters.PARAMETER_EXPRESSION,
                         parameters.PARAMETER_POINT,
                         parameters.PARAMETER_CRS,
                         parameters.PARAMETER_ENUM,
                         parameters.PARAMETER_MATRIX):
            return True
        elif isinstance(param, (QgsProcessingParameterField,
                                QgsProcessingParameterBand,
                                QgsProcessingParameterFeatureSource,
                                QgsProcessingParameterVectorLayer,
                                QgsProcessingParameterMultipleLayers,
                                QgsProcessingParameterNumber,
                                QgsProcessingParameterDistance,
                                QgsProcessingParameterScale,
                                QgsProcessingParameterExpression,
                                QgsProcessingParameterPoint,
                                QgsProcessingParameterCrs,
                                QgsProcessingParameterEnum,
                                QgsProcessingParameterMatrix,
                                QgsProcessingDestinationParameter)):
            return True

        # yay, use new API!
        return False

    def __init__(self, alg, paramType=None, param=None):
        self.alg = alg
        self.paramType = paramType
        self.param = param
        QDialog.__init__(self)
        self.setModal(True)
        self.setupUi()
        settings = QgsSettings()
        self.restoreGeometry(settings.value("/Processing/modelParametersDefinitionDialogGeometry", QByteArray()))

    def closeEvent(self, event):
        settings = QgsSettings()
        settings.setValue("/Processing/modelParametersDefinitionDialogGeometry", self.saveGeometry())
        super(ModelerParameterDefinitionDialog, self).closeEvent(event)

    def setupUi(self):
        type_metadata = QgsApplication.processingRegistry().parameterType(
            self.param.type() if self.param else self.paramType)
        self.setWindowTitle(self.tr('{} Parameter Definition').format(type_metadata.name()))
        self.setMinimumWidth(300)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setMargin(20)

        self.label = QLabel(self.tr('Parameter name'))
        self.verticalLayout.addWidget(self.label)
        self.nameTextBox = QLineEdit()
        self.verticalLayout.addWidget(self.nameTextBox)

        if isinstance(self.param, QgsProcessingParameterDefinition):
            self.nameTextBox.setText(self.param.description())

        if self.paramType == parameters.PARAMETER_TABLE_FIELD or \
                isinstance(self.param, QgsProcessingParameterField):
            self.verticalLayout.addWidget(QLabel(self.tr('Parent layer')))
            self.parentCombo = QComboBox()
            idx = 0
            for param in list(self.alg.parameterComponents().values()):
                definition = self.alg.parameterDefinition(param.parameterName())
                if isinstance(definition, (QgsProcessingParameterFeatureSource, QgsProcessingParameterVectorLayer)):
                    self.parentCombo.addItem(definition.description(), definition.name())
                    if self.param is not None:
                        if self.param.parentLayerParameterName() == definition.name():
                            self.parentCombo.setCurrentIndex(idx)
                    idx += 1
            self.verticalLayout.addWidget(self.parentCombo)

            # add the datatype selector
            self.verticalLayout.addWidget(QLabel(self.tr('Allowed data type')))
            self.datatypeCombo = QComboBox()
            self.datatypeCombo.addItem(self.tr('Any'), -1)
            self.datatypeCombo.addItem(self.tr('Number'), 0)
            self.datatypeCombo.addItem(self.tr('String'), 1)
            self.datatypeCombo.addItem(self.tr('Date/time'), 2)
            self.verticalLayout.addWidget(self.datatypeCombo)

            if self.param is not None and self.param.dataType() is not None:
                # QComboBoxes indexes start at 0,
                # self.param.datatype start with -1 that is why I need to do +1
                datatypeIndex = self.param.dataType() + 1
                self.datatypeCombo.setCurrentIndex(datatypeIndex)

            self.multipleCheck = QCheckBox()
            self.multipleCheck.setText(self.tr('Accept multiple fields'))
            self.multipleCheck.setChecked(False)
            if self.param is not None:
                self.multipleCheck.setChecked(self.param.allowMultiple())
            self.verticalLayout.addWidget(self.multipleCheck)

            self.verticalLayout.addWidget(QLabel(self.tr('Default value')))
            self.defaultTextBox = QLineEdit()
            self.defaultTextBox.setToolTip(
                self.tr('Default field name, or ; separated list of field names for multiple field parameters'))
            if self.param is not None:
                default = self.param.defaultValue()
                if default is not None:
                    self.defaultTextBox.setText(str(default))
            self.verticalLayout.addWidget(self.defaultTextBox)

        elif self.paramType == parameters.PARAMETER_BAND or \
                isinstance(self.param, QgsProcessingParameterBand):
            self.verticalLayout.addWidget(QLabel(self.tr('Parent layer')))
            self.parentCombo = QComboBox()
            idx = 0
            for param in list(self.alg.parameterComponents().values()):
                definition = self.alg.parameterDefinition(param.parameterName())
                if isinstance(definition, (QgsProcessingParameterRasterLayer)):
                    self.parentCombo.addItem(definition.description(), definition.name())
                    if self.param is not None:
                        if self.param.parentLayerParameterName() == definition.name():
                            self.parentCombo.setCurrentIndex(idx)
                    idx += 1
            self.verticalLayout.addWidget(self.parentCombo)
        elif (self.paramType in (
                parameters.PARAMETER_VECTOR, parameters.PARAMETER_TABLE) or
              isinstance(self.param, (QgsProcessingParameterFeatureSource, QgsProcessingParameterVectorLayer))):
            self.verticalLayout.addWidget(QLabel(self.tr('Geometry type')))
            self.shapetypeCombo = QComboBox()
            self.shapetypeCombo.addItem(self.tr('Geometry Not Required'), QgsProcessing.TypeVector)
            self.shapetypeCombo.addItem(self.tr('Point'), QgsProcessing.TypeVectorPoint)
            self.shapetypeCombo.addItem(self.tr('Line'), QgsProcessing.TypeVectorLine)
            self.shapetypeCombo.addItem(self.tr('Polygon'), QgsProcessing.TypeVectorPolygon)
            self.shapetypeCombo.addItem(self.tr('Any Geometry Type'), QgsProcessing.TypeVectorAnyGeometry)
            if self.param is not None:
                self.shapetypeCombo.setCurrentIndex(self.shapetypeCombo.findData(self.param.dataTypes()[0]))
            self.verticalLayout.addWidget(self.shapetypeCombo)
        elif (self.paramType == parameters.PARAMETER_MULTIPLE or
              isinstance(self.param, QgsProcessingParameterMultipleLayers)):
            self.verticalLayout.addWidget(QLabel(self.tr('Data type')))
            self.datatypeCombo = QComboBox()
            self.datatypeCombo.addItem(self.tr('Any Map Layer'), QgsProcessing.TypeMapLayer)
            self.datatypeCombo.addItem(self.tr('Vector (No Geometry Required)'), QgsProcessing.TypeVector)
            self.datatypeCombo.addItem(self.tr('Vector (Point)'), QgsProcessing.TypeVectorPoint)
            self.datatypeCombo.addItem(self.tr('Vector (Line)'), QgsProcessing.TypeVectorLine)
            self.datatypeCombo.addItem(self.tr('Vector (Polygon)'), QgsProcessing.TypeVectorPolygon)
            self.datatypeCombo.addItem(self.tr('Vector (Any Geometry Type)'), QgsProcessing.TypeVectorAnyGeometry)
            self.datatypeCombo.addItem(self.tr('Raster'), QgsProcessing.TypeRaster)
            self.datatypeCombo.addItem(self.tr('File'), QgsProcessing.TypeFile)
            if self.param is not None:
                self.datatypeCombo.setCurrentIndex(self.datatypeCombo.findData(self.param.layerType()))
            self.verticalLayout.addWidget(self.datatypeCombo)
        elif (self.paramType in (
        parameters.PARAMETER_NUMBER, parameters.PARAMETER_DISTANCE, parameters.PARAMETER_SCALE) or
              isinstance(self.param,
                         (QgsProcessingParameterNumber, QgsProcessingParameterDistance, QgsProcessingParameterScale))):

            if (self.paramType == parameters.PARAMETER_DISTANCE or
                    isinstance(self.param, QgsProcessingParameterDistance)):
                self.verticalLayout.addWidget(QLabel(self.tr('Linked input')))
                self.parentCombo = QComboBox()
                self.parentCombo.addItem('', '')
                idx = 1
                for param in list(self.alg.parameterComponents().values()):
                    definition = self.alg.parameterDefinition(param.parameterName())
                    if isinstance(definition, (QgsProcessingParameterFeatureSource,
                                               QgsProcessingParameterVectorLayer,
                                               QgsProcessingParameterMapLayer,
                                               QgsProcessingParameterCrs)):
                        self.parentCombo.addItem(definition.description(), definition.name())
                        if self.param is not None:
                            if self.param.parentParameterName() == definition.name():
                                self.parentCombo.setCurrentIndex(idx)
                        idx += 1
                self.verticalLayout.addWidget(self.parentCombo)
            elif (self.paramType != parameters.PARAMETER_SCALE and not
            isinstance(self.param, QgsProcessingParameterScale)):
                self.verticalLayout.addWidget(QLabel(self.tr('Number type')))
                self.type_combo = QComboBox()
                self.type_combo.addItem(self.tr('Float'), QgsProcessingParameterNumber.Double)
                self.type_combo.addItem(self.tr('Integer'), QgsProcessingParameterNumber.Integer)
                if self.param:
                    self.type_combo.setCurrentIndex(self.type_combo.findData(self.param.dataType()))
                self.verticalLayout.addWidget(self.type_combo)

            if (self.paramType != parameters.PARAMETER_SCALE and not
            isinstance(self.param, QgsProcessingParameterScale)):
                self.verticalLayout.addWidget(QLabel(self.tr('Min value')))
                self.minTextBox = QLineEdit()
                self.verticalLayout.addWidget(self.minTextBox)
                self.verticalLayout.addWidget(QLabel(self.tr('Max value')))
                self.maxTextBox = QLineEdit()
                self.verticalLayout.addWidget(self.maxTextBox)
                if self.param is not None:
                    self.minTextBox.setText(str(self.param.minimum()))
                    self.maxTextBox.setText(str(self.param.maximum()))
            self.verticalLayout.addWidget(QLabel(self.tr('Default value')))
            self.defaultTextBox = QLineEdit()
            self.defaultTextBox.setText(self.tr('0'))
            if self.param is not None:
                default = self.param.defaultValue()
                if self.param.dataType() == QgsProcessingParameterNumber.Integer:
                    default = int(math.floor(float(default)))
                if default:
                    self.defaultTextBox.setText(str(default))
            self.verticalLayout.addWidget(self.defaultTextBox)
        elif (self.paramType == parameters.PARAMETER_EXPRESSION or
              isinstance(self.param, QgsProcessingParameterExpression)):
            self.verticalLayout.addWidget(QLabel(self.tr('Default value')))
            self.defaultEdit = QgsExpressionLineEdit()
            if self.param is not None:
                self.defaultEdit.setExpression(self.param.defaultValue())
            self.verticalLayout.addWidget(self.defaultEdit)

            self.verticalLayout.addWidget(QLabel(self.tr('Parent layer')))
            self.parentCombo = QComboBox()
            self.parentCombo.addItem(self.tr("None"), None)
            idx = 1
            for param in list(self.alg.parameterComponents().values()):
                definition = self.alg.parameterDefinition(param.parameterName())
                if isinstance(definition, (QgsProcessingParameterFeatureSource, QgsProcessingParameterVectorLayer)):
                    self.parentCombo.addItem(definition.description(), definition.name())
                    if self.param is not None:
                        if self.param.parentLayerParameterName() == definition.name():
                            self.parentCombo.setCurrentIndex(idx)
                    idx += 1
            self.verticalLayout.addWidget(self.parentCombo)
        elif (self.paramType == parameters.PARAMETER_POINT or
              isinstance(self.param, QgsProcessingParameterPoint)):
            self.verticalLayout.addWidget(QLabel(self.tr('Default value')))
            self.defaultTextBox = QLineEdit()
            if self.param is not None:
                self.defaultTextBox.setText(self.param.defaultValue())
            self.verticalLayout.addWidget(self.defaultTextBox)
        elif (self.paramType == parameters.PARAMETER_CRS or
              isinstance(self.param, QgsProcessingParameterCrs)):
            self.verticalLayout.addWidget(QLabel(self.tr('Default value')))
            self.selector = QgsProjectionSelectionWidget()
            if self.param is not None:
                self.selector.setCrs(QgsCoordinateReferenceSystem(self.param.defaultValue()))
            else:
                self.selector.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
            self.verticalLayout.addWidget(self.selector)
        elif self.paramType == parameters.PARAMETER_ENUM or \
                isinstance(self.param, QgsProcessingParameterEnum):
            self.widget = EnumModelerWidget(self)
            if self.param is not None:
                self.widget.setAllowMultiple(bool(self.param.allowMultiple()))
                self.widget.setOptions(self.param.options())
                self.widget.setDefault(self.param.defaultValue())
            self.verticalLayout.addWidget(self.widget)
        elif self.paramType == parameters.PARAMETER_MATRIX or \
                isinstance(self.param, QgsProcessingParameterMatrix):
            self.widget = MatrixModelerWidget(self)
            if self.param is not None:
                self.widget.setValue(self.param.headers(), self.param.defaultValue())
                self.widget.setFixedRows(self.param.hasFixedNumberRows())
            self.verticalLayout.addWidget(self.widget)

        elif isinstance(self.param, QgsProcessingDestinationParameter):
            self.verticalLayout.addWidget(QLabel(self.tr('Default value')))
            self.defaultWidget = DestinationSelectionPanel(self.param, self.alg, default_selection=True)
            self.verticalLayout.addWidget(self.defaultWidget)

        self.verticalLayout.addSpacing(20)
        self.requiredCheck = QCheckBox()
        self.requiredCheck.setText(self.tr('Mandatory'))
        self.requiredCheck.setChecked(True)
        if self.param is not None:
            self.requiredCheck.setChecked(not self.param.flags() & QgsProcessingParameterDefinition.FlagOptional)
        self.verticalLayout.addWidget(self.requiredCheck)

        self.advancedCheck = QCheckBox()
        self.advancedCheck.setText(self.tr('Advanced'))
        self.advancedCheck.setChecked(False)
        if self.param is not None:
            self.advancedCheck.setChecked(self.param.flags() & QgsProcessingParameterDefinition.FlagAdvanced)
        self.verticalLayout.addWidget(self.advancedCheck)

        # If child algorithm output is mandatory, disable checkbox
        if isinstance(self.param, QgsProcessingDestinationParameter):
            provider_name, child_name, output_name = self.param.name().split(':')
            child = self.alg.childAlgorithms()['{}:{}'.format(provider_name, child_name)]
            model_output = child.modelOutput(output_name)
            param_def = child.algorithm().parameterDefinition(model_output.childOutputName())
            if not (param_def.flags() & QgsProcessingParameterDefinition.FlagOptional):
                self.requiredCheck.setEnabled(False)
                self.requiredCheck.setChecked(True)

            self.advancedCheck.setEnabled(False)
            self.advancedCheck.setChecked(False)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel |
                                          QDialogButtonBox.Ok)
        self.buttonBox.setObjectName('buttonBox')
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.verticalLayout.addStretch()
        self.verticalLayout.addWidget(self.buttonBox)

        self.setLayout(self.verticalLayout)

    def accept(self):
        description = self.nameTextBox.text()
        if description.strip() == '':
            QMessageBox.warning(self, self.tr('Unable to define parameter'),
                                self.tr('Invalid parameter name'))
            return
        if self.param is None:
            validChars = \
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            safeName = ''.join(c for c in description if c in validChars)
            name = safeName.lower()
            i = 2
            while self.alg.parameterDefinition(name):
                name = safeName.lower() + str(i)
                i += 1
        else:
            name = self.param.name()
        if (self.paramType == parameters.PARAMETER_TABLE_FIELD or
                isinstance(self.param, QgsProcessingParameterField)):
            if self.parentCombo.currentIndex() < 0:
                QMessageBox.warning(self, self.tr('Unable to define parameter'),
                                    self.tr('Wrong or missing parameter values'))
                return
            parent = self.parentCombo.currentData()
            datatype = self.datatypeCombo.currentData()
            default = self.defaultTextBox.text()
            if not default:
                default = None
            self.param = QgsProcessingParameterField(name, description, defaultValue=default,
                                                     parentLayerParameterName=parent, type=datatype,
                                                     allowMultiple=self.multipleCheck.isChecked())
        elif (self.paramType == parameters.PARAMETER_BAND or
              isinstance(self.param, QgsProcessingParameterBand)):
            if self.parentCombo.currentIndex() < 0:
                QMessageBox.warning(self, self.tr('Unable to define parameter'),
                                    self.tr('Wrong or missing parameter values'))
                return
            parent = self.parentCombo.currentData()
            self.param = QgsProcessingParameterBand(name, description, None, parent)
        elif (self.paramType == parameters.PARAMETER_MAP_LAYER or
              isinstance(self.param, QgsProcessingParameterMapLayer)):
            self.param = QgsProcessingParameterMapLayer(
                name, description)
        elif (self.paramType == parameters.PARAMETER_RASTER or
              isinstance(self.param, QgsProcessingParameterRasterLayer)):
            self.param = QgsProcessingParameterRasterLayer(
                name, description)
        elif (self.paramType == parameters.PARAMETER_TABLE or
              isinstance(self.param, QgsProcessingParameterVectorLayer)):
            self.param = QgsProcessingParameterVectorLayer(
                name, description,
                [self.shapetypeCombo.currentData()])
        elif (self.paramType == parameters.PARAMETER_VECTOR or
              isinstance(self.param, QgsProcessingParameterFeatureSource)):
            self.param = QgsProcessingParameterFeatureSource(
                name, description,
                [self.shapetypeCombo.currentData()])
        elif (self.paramType == parameters.PARAMETER_MULTIPLE or
              isinstance(self.param, QgsProcessingParameterMultipleLayers)):
            self.param = QgsProcessingParameterMultipleLayers(
                name, description,
                self.datatypeCombo.currentData())
        elif (self.paramType == parameters.PARAMETER_DISTANCE or
              isinstance(self.param, QgsProcessingParameterDistance)):
            self.param = QgsProcessingParameterDistance(name, description,
                                                        self.defaultTextBox.text())
            try:
                vmin = self.minTextBox.text().strip()
                if not vmin == '':
                    self.param.setMinimum(float(vmin))
                vmax = self.maxTextBox.text().strip()
                if not vmax == '':
                    self.param.setMaximum(float(vmax))
            except:
                QMessageBox.warning(self, self.tr('Unable to define parameter'),
                                    self.tr('Wrong or missing parameter values'))
                return

            if self.parentCombo.currentIndex() < 0:
                QMessageBox.warning(self, self.tr('Unable to define parameter'),
                                    self.tr('Wrong or missing parameter values'))
                return
            parent = self.parentCombo.currentData()
            if parent:
                self.param.setParentParameterName(parent)
        elif (self.paramType == parameters.PARAMETER_SCALE or
              isinstance(self.param, QgsProcessingParameterScale)):
            self.param = QgsProcessingParameterScale(name, description,
                                                     self.defaultTextBox.text())
        elif (self.paramType == parameters.PARAMETER_NUMBER or
              isinstance(self.param, QgsProcessingParameterNumber)):

            type = self.type_combo.currentData()
            self.param = QgsProcessingParameterNumber(name, description, type,
                                                      self.defaultTextBox.text())
            try:
                vmin = self.minTextBox.text().strip()
                if not vmin == '':
                    self.param.setMinimum(float(vmin))
                vmax = self.maxTextBox.text().strip()
                if not vmax == '':
                    self.param.setMaximum(float(vmax))
            except:
                QMessageBox.warning(self, self.tr('Unable to define parameter'),
                                    self.tr('Wrong or missing parameter values'))
                return
        elif (self.paramType == parameters.PARAMETER_EXPRESSION or
              isinstance(self.param, QgsProcessingParameterExpression)):
            parent = self.parentCombo.currentData()
            self.param = QgsProcessingParameterExpression(name, description,
                                                          str(self.defaultEdit.expression()),
                                                          parent)
        elif (self.paramType == parameters.PARAMETER_EXTENT or
              isinstance(self.param, QgsProcessingParameterExtent)):
            self.param = QgsProcessingParameterExtent(name, description)
        elif (self.paramType == parameters.PARAMETER_POINT or
              isinstance(self.param, QgsProcessingParameterPoint)):
            self.param = QgsProcessingParameterPoint(name, description,
                                                     str(self.defaultTextBox.text()))
        elif (self.paramType == parameters.PARAMETER_CRS or
              isinstance(self.param, QgsProcessingParameterCrs)):
            self.param = QgsProcessingParameterCrs(name, description, self.selector.crs().authid())
        elif (self.paramType == parameters.PARAMETER_ENUM or
              isinstance(self.param, QgsProcessingParameterEnum)):
            self.param = QgsProcessingParameterEnum(name, description, self.widget.options(),
                                                    self.widget.allowMultiple(), self.widget.defaultOptions())
        elif (self.paramType == parameters.PARAMETER_MATRIX or
              isinstance(self.param, QgsProcessingParameterMatrix)):
            self.param = QgsProcessingParameterMatrix(name, description, hasFixedNumberRows=self.widget.fixedRows(),
                                                      headers=self.widget.headers(), defaultValue=self.widget.value())

        # Destination parameter
        elif (isinstance(self.param, QgsProcessingParameterFeatureSink)):
            self.param = QgsProcessingParameterFeatureSink(
                name=name,
                description=self.param.description(),
                type=self.param.dataType(),
                defaultValue=self.defaultWidget.getValue())
        elif (isinstance(self.param, QgsProcessingParameterFileDestination)):
            self.param = QgsProcessingParameterFileDestination(
                name=name,
                description=self.param.description(),
                fileFilter=self.param.fileFilter(),
                defaultValue=self.defaultWidget.getValue())
        elif (isinstance(self.param, QgsProcessingParameterFolderDestination)):
            self.param = QgsProcessingParameterFolderDestination(
                name=name,
                description=self.param.description(),
                defaultValue=self.defaultWidget.getValue())
        elif (isinstance(self.param, QgsProcessingParameterRasterDestination)):
            self.param = QgsProcessingParameterRasterDestination(
                name=name,
                description=self.param.description(),
                defaultValue=self.defaultWidget.getValue())
        elif (isinstance(self.param, QgsProcessingParameterVectorDestination)):
            self.param = QgsProcessingParameterVectorDestination(
                name=name,
                description=self.param.description(),
                type=self.param.dataType(),
                defaultValue=self.defaultWidget.getValue())

        else:
            if self.paramType:
                typeId = self.paramType
            else:
                typeId = self.param.type()

            paramTypeDef = QgsApplication.instance().processingRegistry().parameterType(typeId)
            if not paramTypeDef:
                msg = self.tr('The parameter `{}` is not registered, are you missing a required plugin?'.format(typeId))
                raise UndefinedParameterException(msg)
            self.param = paramTypeDef.create(name)
            self.param.setDescription(description)
            self.param.setMetadata(paramTypeDef.metadata())

        if not self.requiredCheck.isChecked():
            self.param.setFlags(self.param.flags() | QgsProcessingParameterDefinition.FlagOptional)
        else:
            self.param.setFlags(self.param.flags() & ~QgsProcessingParameterDefinition.FlagOptional)

        if self.advancedCheck.isChecked():
            self.param.setFlags(self.param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        else:
            self.param.setFlags(self.param.flags() & ~QgsProcessingParameterDefinition.FlagAdvanced)

        settings = QgsSettings()
        settings.setValue("/Processing/modelParametersDefinitionDialogGeometry", self.saveGeometry())

        QDialog.accept(self)

    def reject(self):
        self.param = None

        settings = QgsSettings()
        settings.setValue("/Processing/modelParametersDefinitionDialogGeometry", self.saveGeometry())

        QDialog.reject(self)
