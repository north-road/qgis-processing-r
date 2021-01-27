# -*- coding: utf-8 -*-

"""
***************************************************************************
    provider.py
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
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (Qgis,
                       QgsProcessingProvider,
                       QgsMessageLog)

from processing.core.ProcessingConfig import ProcessingConfig, Setting
from processing.gui.ProviderActions import (ProviderActions,
                                            ProviderContextMenuActions)

from processing_r.processing.actions.create_new_script import CreateNewScriptAction
from processing_r.processing.actions.edit_script import EditScriptAction
from processing_r.processing.actions.delete_script import DeleteScriptAction
from processing_r.processing.exceptions import InvalidScriptException
from processing_r.processing.utils import RUtils
from processing_r.processing.algorithm import RAlgorithm
from processing_r.gui.gui_utils import GuiUtils


class RAlgorithmProvider(QgsProcessingProvider):
    """
    Processing provider for executing R scripts
    """

    VERSION = '2.3.0'

    def __init__(self):
        super().__init__()
        self.algs = []
        self.actions = []
        create_script_action = CreateNewScriptAction()
        self.actions.append(create_script_action)
        self.contextMenuActions = [EditScriptAction(),
                                   DeleteScriptAction()]

        self.r_version = None

    def load(self):
        """
        Called when first loading provider
        """
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(
            self.name(), RUtils.RSCRIPTS_FOLDER,
            self.tr('R scripts folder'), RUtils.default_scripts_folder(),
            valuetype=Setting.MULTIPLE_FOLDERS))

        ProcessingConfig.addSetting(Setting(self.name(), RUtils.R_USE_USER_LIB,
                                            self.tr('Use user library folder instead of system libraries'), True))
        ProcessingConfig.addSetting(Setting(
            self.name(),
            RUtils.R_LIBS_USER, self.tr('User library folder'),
            RUtils.r_library_folder(), valuetype=Setting.FOLDER))

        ProcessingConfig.addSetting(Setting(
            self.name(),
            RUtils.R_REPO, self.tr('Package repository'),
            "http://cran.at.r-project.org/", valuetype=Setting.STRING))

        ProcessingConfig.addSetting(Setting(
            self.name(),
            RUtils.R_FOLDER, self.tr('R folder'), RUtils.r_binary_folder(),
            valuetype=Setting.FOLDER))

        if RUtils.is_windows():
            ProcessingConfig.addSetting(Setting(
                self.name(),
                RUtils.R_USE64, self.tr('Use 64 bit version'), False))

        ProviderActions.registerProviderActions(self, self.actions)
        ProviderContextMenuActions.registerProviderContextMenuActions(self.contextMenuActions)
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        self.r_version = RUtils.get_r_version()
        return True

    def unload(self):
        """
        Called when unloading provider
        """
        ProcessingConfig.removeSetting(RUtils.RSCRIPTS_FOLDER)
        ProcessingConfig.removeSetting(RUtils.R_LIBS_USER)
        ProcessingConfig.removeSetting(RUtils.R_FOLDER)
        if RUtils.is_windows():
            ProcessingConfig.removeSetting(RUtils.R_USE64)
        ProviderActions.deregisterProviderActions(self)
        ProviderContextMenuActions.deregisterProviderContextMenuActions(self.contextMenuActions)

    def icon(self):
        """
        Returns the provider's icon
        """
        return GuiUtils.get_icon("providerR.svg")

    def svgIconPath(self):
        """
        Returns a path to the provider's icon as a SVG file
        """
        return GuiUtils.get_icon_svg("providerR.svg")

    def name(self):
        """
        Display name for provider
        """
        return self.tr('R')

    def versionInfo(self):
        """
        Provider plugin version
        """
        if not self.r_version:
            return "QGIS R Provider version {}".format(self.VERSION)

        return "QGIS R Provider version {}, {}".format(self.VERSION, self.r_version)

    def id(self):
        """
        Unique ID for provider
        """
        return 'r'

    def loadAlgorithms(self):
        """
        Called when provider must populate its available algorithms
        """
        algs = []
        for f in RUtils.script_folders():
            algs.extend(self.load_scripts_from_folder(f))

        for a in algs:
            self.addAlgorithm(a)

    def load_scripts_from_folder(self, folder):
        """
        Loads all scripts found under the specified sub-folder
        """
        if not os.path.exists(folder):
            return []

        algs = []
        for path, _, files in os.walk(folder):
            for description_file in files:
                if description_file.lower().endswith('rsx'):
                    try:
                        fullpath = os.path.join(path, description_file)
                        alg = RAlgorithm(fullpath)
                        if alg.name().strip():
                            algs.append(alg)
                    except InvalidScriptException as e:
                        QgsMessageLog.logMessage(e.msg, self.tr('Processing'), Qgis.Critical)
                    except Exception as e:  # pylint: disable=broad-except
                        QgsMessageLog.logMessage(
                            self.tr('Could not load R script: {0}\n{1}').format(description_file, str(e)),
                            self.tr('Processing'), Qgis.Critical)
        return algs

    def tr(self, string, context=''):
        """
        Translates a string
        """
        if context == '':
            context = 'RAlgorithmProvider'
        return QCoreApplication.translate(context, string)

    def supportedOutputTableExtensions(self):
        """
        Extensions for non-spatial vector outputs
        """
        return ['csv']

    def defaultVectorFileExtension(self, hasGeometry=True):
        """
        Default extension -- we use Geopackage for spatial layers, CSV for non-spatial layers
        """
        return 'gpkg' if hasGeometry else 'csv'

    def supportsNonFileBasedOutput(self):
        """
        Provider cannot handle memory layers/db sources
        """
        return False
