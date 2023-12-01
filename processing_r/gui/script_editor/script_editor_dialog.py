# -*- coding: utf-8 -*-

"""
***************************************************************************
    EditScriptDialog.py
    ---------------------
    Date                 : December 2012
    Copyright            : (C) 2012 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'December 2012'
__copyright__ = '(C) 2012, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import codecs
import inspect
import traceback
import warnings
from functools import partial

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QCursor
from qgis.PyQt.QtWidgets import (QMessageBox,
                                 QFileDialog,
                                 QMenu,
                                 QAction,
                                 QToolButton)

from qgis.gui import QgsGui, QgsErrorDialog
from qgis.core import (QgsApplication,
                       QgsSettings,
                       QgsError,
                       QgsProcessingAlgorithm,
                       QgsProcessingFeatureBasedAlgorithm,
                       QgsProcessingParameterType)
from qgis.utils import iface, OverrideCursor
# from qgis.processing import alg as algfactory

from processing.gui.AlgorithmDialog import AlgorithmDialog
from processing.script import ScriptUtils

from processing_r.processing.utils import RUtils
from processing_r.processing.algorithm import RAlgorithm
from processing_r.gui.gui_utils import GuiUtils
from processing_r.gui.script_editor.parameter_definition_dialog import create_new_parameter

pluginPath = os.path.split(os.path.dirname(__file__))[0]

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    WIDGET, BASE = uic.loadUiType(
        GuiUtils.get_ui_file_path('DlgScriptEditor.ui'))


# This class is ported from the QGIS core Processing script editor.
# Unfortunately generalising the core editor to allow everything we want in an R editor
# isn't feasible... so lots of duplicate code here :(
# Try to keep the diff between the two as small as possible, to allow porting fixes from QGIS core


class ScriptEditorDialog(BASE, WIDGET):
    hasChanged = False

    def __init__(self, filePath=None, parent=None):
        super(ScriptEditorDialog, self).__init__(parent)
        self.setupUi(self)

        QgsGui.instance().enableAutoGeometryRestore(self)

        self.editor.initLexer()
        self.searchWidget.setVisible(False)

        if iface is not None:
            self.toolBar.setIconSize(iface.iconSize())
            self.setStyleSheet(iface.mainWindow().styleSheet())

        self.actionOpenScript.setIcon(
            QgsApplication.getThemeIcon('/mActionScriptOpen.svg'))
        self.actionSaveScript.setIcon(
            QgsApplication.getThemeIcon('/mActionFileSave.svg'))
        self.actionSaveScriptAs.setIcon(
            QgsApplication.getThemeIcon('/mActionFileSaveAs.svg'))
        self.actionRunScript.setIcon(
            QgsApplication.getThemeIcon('/mActionStart.svg'))
        self.actionCut.setIcon(
            QgsApplication.getThemeIcon('/mActionEditCut.svg'))
        self.actionCopy.setIcon(
            QgsApplication.getThemeIcon('/mActionEditCopy.svg'))
        self.actionPaste.setIcon(
            QgsApplication.getThemeIcon('/mActionEditPaste.svg'))
        self.actionUndo.setIcon(
            QgsApplication.getThemeIcon('/mActionUndo.svg'))
        self.actionRedo.setIcon(
            QgsApplication.getThemeIcon('/mActionRedo.svg'))
        self.actionFindReplace.setIcon(
            QgsApplication.getThemeIcon('/mActionFindReplace.svg'))
        self.actionIncreaseFontSize.setIcon(
            QgsApplication.getThemeIcon('/mActionIncreaseFont.svg'))
        self.actionDecreaseFontSize.setIcon(
            QgsApplication.getThemeIcon('/mActionDecreaseFont.svg'))

        # Connect signals and slots
        self.actionOpenScript.triggered.connect(self.openScript)
        self.actionSaveScript.triggered.connect(self.save)
        self.actionSaveScriptAs.triggered.connect(self.saveAs)
        self.actionRunScript.triggered.connect(self.runAlgorithm)
        self.actionCut.triggered.connect(self.editor.cut)
        self.actionCopy.triggered.connect(self.editor.copy)
        self.actionPaste.triggered.connect(self.editor.paste)
        self.actionUndo.triggered.connect(self.editor.undo)
        self.actionRedo.triggered.connect(self.editor.redo)
        self.actionFindReplace.toggled.connect(self.toggleSearchBox)
        self.actionIncreaseFontSize.triggered.connect(self.editor.zoomIn)
        self.actionDecreaseFontSize.triggered.connect(self.editor.zoomOut)
        self.editor.textChanged.connect(lambda: self.setHasChanged(True))

        self.leFindText.returnPressed.connect(self.find)
        self.btnFind.clicked.connect(self.find)
        self.btnReplace.clicked.connect(self.replace)
        self.lastSearch = None

        self.filePath = None
        if filePath is not None:
            self._loadFile(filePath)

        self.setHasChanged(False)

        # new code - not in QGIS master
        self.new_parameter_menu = QMenu()
        sorted_parameter_types = sorted(QgsApplication.instance().processingRegistry().parameterTypes(), key=lambda pt: pt.name())
        for param in sorted_parameter_types:
            if param.flags() & QgsProcessingParameterType.ExposeToModeler:
                new_parameter_action = QAction(param.name(), parent=self.new_parameter_menu)
                new_parameter_action.triggered.connect(partial(self.add_parameter,param.id()))
                self.new_parameter_menu.addAction(new_parameter_action)

        self.add_parameter_button = QToolButton()
        self.add_parameter_button.setText(self.tr('Add Input Parameter'))
        self.add_parameter_button.setPopupMode(QToolButton.InstantPopup)
        self.add_parameter_button.setMenu(self.new_parameter_menu)
        self.toolBar.addWidget(self.add_parameter_button)

    def add_parameter(self, parameter_type):
        """
        Allows users to create a new parameter of a given type
        """
        param = create_new_parameter(parameter_type, script_contents=self.editor.text())
        if param is None:
            return

        definition = param.asScriptCode() + '\n'
        self.editor.insert(definition)

    def update_dialog_title(self):
        """
        Updates the script editor dialog title
        """
        if self.filePath:
            path, file_name = os.path.split(self.filePath)
        else:
            file_name = self.tr('Untitled Script')

        if self.hasChanged:
            file_name = '*' + file_name

        self.setWindowTitle(self.tr('{} - R Script Editor').format(file_name))

    def closeEvent(self, event):
        settings = QgsSettings()
        settings.setValue("/Processing/stateScriptEditor", self.saveState())
        settings.setValue("/Processing/geometryScriptEditor", self.saveGeometry())

        if self.hasChanged:
            ret = QMessageBox.question(
                self, self.tr('Save Script?'),
                self.tr('There are unsaved changes in this script. Do you want to keep those?'),
                QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Discard, QMessageBox.Cancel)

            if ret == QMessageBox.Save:
                self.saveScript(False)
                event.accept()
            elif ret == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def openScript(self):
        if self.hasChanged:
            ret = QMessageBox.warning(self,
                                      self.tr("Unsaved changes"),
                                      self.tr("There are unsaved changes in the script. Continue?"),
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ret == QMessageBox.No:
                return

        scriptDir = RUtils.default_scripts_folder()
        fileName, _ = QFileDialog.getOpenFileName(self,
                                                  self.tr("Open script"),
                                                  scriptDir,
                                                  self.tr("R scripts (*.rsx *.RSX)"))

        if fileName == "":
            return

        with OverrideCursor(Qt.WaitCursor):
            self._loadFile(fileName)

    def save(self):
        self.saveScript(False)

    def saveAs(self):
        self.saveScript(True)

    def saveScript(self, saveAs):
        newPath = None
        if self.filePath is None or saveAs:
            scriptDir = RUtils.default_scripts_folder()
            newPath, _ = QFileDialog.getSaveFileName(self,
                                                     self.tr("Save script"),
                                                     scriptDir,
                                                     self.tr("R scripts (*.rsx *.RSX)"))

            if newPath:
                if not newPath.lower().endswith(".rsx"):
                    newPath += ".rsx"

                self.filePath = newPath

        if self.filePath:
            text = self.editor.text()
            try:
                with codecs.open(self.filePath, "w", encoding="utf-8") as f:
                    f.write(text)
            except IOError as e:
                QMessageBox.warning(self,
                                    self.tr("I/O error"),
                                    self.tr("Unable to save edits:\n{}").format(str(e))
                                    )
                return

            self.setHasChanged(False)

        QgsApplication.processingRegistry().providerById("r").refreshAlgorithms()

    def setHasChanged(self, hasChanged):
        self.hasChanged = hasChanged
        self.actionSaveScript.setEnabled(hasChanged)
        self.update_dialog_title()

    def runAlgorithm(self):
        alg = RAlgorithm(description_file=None, script=self.editor.text())
        if alg.error is not None:
            error = QgsError(alg.error, "R")
            QgsErrorDialog.show(error,
                                self.tr("Execution error")
                                )
            return

        alg.setProvider(QgsApplication.processingRegistry().providerById("r"))
        alg.initAlgorithm()

        dlg = alg.createCustomParametersWidget(iface.mainWindow())
        if not dlg:
            dlg = AlgorithmDialog(alg, parent=iface.mainWindow())

        canvas = iface.mapCanvas()
        prevMapTool = canvas.mapTool()

        dlg.show()

        if canvas.mapTool() != prevMapTool:
            if canvas.mapTool():
                canvas.mapTool().reset()
            canvas.setMapTool(prevMapTool)

    def find(self):
        textToFind = self.leFindText.text()
        caseSensitive = self.chkCaseSensitive.isChecked()
        wholeWord = self.chkWholeWord.isChecked()
        if self.lastSearch is None or textToFind != self.lastSearch:
            self.editor.findFirst(textToFind, False, caseSensitive, wholeWord, True)
        else:
            self.editor.findNext()

    def replace(self):
        textToReplace = self.leReplaceText.text()
        self.editor.replaceSelectedText(textToReplace)

    def toggleSearchBox(self, checked):
        self.searchWidget.setVisible(checked)
        if (checked):
            self.leFindText.setFocus()

    def _loadFile(self, filePath):
        with codecs.open(filePath, "r", encoding="utf-8") as f:
            txt = f.read()

        self.editor.setText(txt)
        self.hasChanged = False
        self.editor.setModified(False)
        self.editor.recolor()

        self.filePath = filePath
        self.update_dialog_title()
