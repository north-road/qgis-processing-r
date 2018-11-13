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
from builtins import str

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingProvider
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from r.processing.actions.create_new_script import CreateNewScriptAction
from r.processing.actions.edit_script import EditScriptAction
from r.processing.actions.delete_script import DeleteScriptAction

#from processing.script.WrongScriptException import WrongScriptException
from processing.gui.ProviderActions import (ProviderActions,
                                            ProviderContextMenuActions)
from processing.tools.system import isWindows

from r.processing.utils import RUtils
#from r.processing.algorithm import RAlgorithm
from r.gui.gui_utils import GuiUtils


class RAlgorithmProvider(QgsProcessingProvider):
    """
    Processing provider for executing R scripts
    """

    def __init__(self):
        super().__init__()
        self.algs = []
        self.actions = []
        create_script_action = CreateNewScriptAction()
        self.actions.append(create_script_action)
        self.contextMenuActions = []
        #    [EditScriptAction(EditScriptAction.SCRIPT_R),
        #     DeleteScriptAction(DeleteScriptAction.SCRIPT_R)]

    def load(self):
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(self.name(), 'ACTIVATE_R',
                                            self.tr('Activate'), False))
        ProcessingConfig.addSetting(Setting(
            self.name(), RUtils.RSCRIPTS_FOLDER,
            self.tr('R scripts folder'), RUtils.defaultRScriptsFolder(),
            valuetype=Setting.MULTIPLE_FOLDERS))
        ##if isWindows():
        #    ProcessingConfig.addSetting(Setting(#
        #        self.name(),
        #        RUtils.R_FOLDER, self.tr('R folder'), RUtils.RFolder(),
        #        valuetype=Setting.FOLDER))
        #    ProcessingConfig.addSetting(Setting(
        #        self.name(),
        #        RUtils.R_LIBS_USER, self.tr('R user library folder'),
        #        RUtils.RLibs(), valuetype=Setting.FOLDER))
        #    ProcessingConfig.addSetting(Setting(
        #        self.name(),
        #        RUtils.R_USE64, self.tr('Use 64 bit version'), False))
        ProviderActions.registerProviderActions(self, self.actions)
        ProviderContextMenuActions.registerProviderContextMenuActions(self.contextMenuActions)
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def unload(self):
        ProcessingConfig.removeSetting('ACTIVATE_R')
        ProcessingConfig.removeSetting(RUtils.RSCRIPTS_FOLDER)
       #if isWindows():
       #     ProcessingConfig.removeSetting(RUtils.R_FOLDER)
       #     ProcessingConfig.removeSetting(RUtils.R_LIBS_USER)
       #     ProcessingConfig.removeSetting(RUtils.R_USE64)
        ProviderActions.deregisterProviderActions(self)
        ProviderContextMenuActions.deregisterProviderContextMenuActions(self.contextMenuActions)

    def isActive(self):
        return ProcessingConfig.getSetting('ACTIVATE_R')

    def setActive(self, active):
        ProcessingConfig.setSettingValue('ACTIVATE_R', active)

    def icon(self):
        return GuiUtils.get_icon("providerR.svg")

    def svgIconPath(self):
        return GuiUtils.get_icon_svg("providerR.svg")

    def name(self):
        return self.tr('R scripts')

    def longName(self):
        return self.tr('R scripts')

    def id(self):
        return 'r'

    def loadAlgorithms(self):
        pass
        #folders = RUtils.RScriptsFolders()
        #self.algs = []
        #for f in folders:
        #    self.loadFromFolder(f)
        #
        #folder = os.path.join(os.path.dirname(__file__), 'scripts')
        #self.loadFromFolder(folder)
        #for a in self.algs:
        #    self.addAlgorithm(a)
        #

   # def loadFromFolder(self, folder):
   #     if not os.path.exists(folder):
   #         return
   #     for path, subdirs, files in os.walk(folder):
   #         for descriptionFile in files:
   #             if descriptionFile.endswith('rsx'):
   #                 try:
   #                     fullpath = os.path.join(path, descriptionFile)
   #         #            alg = RAlgorithm(fullpath)
   #                     if alg.name().strip() != '':
   #                         self.algs.append(alg)
   #                 except WrongScriptException as e:
   #                     QgsMessageLog.logMessage(e.msg, self.tr('Processing'), QgsMessageLog.CRITICAL)
   #                 except Exception as e:
   #                     QgsMessageLog.logMessage(
   #                         self.tr('Could not load R script: {0}\n{1}').format(descriptionFile, str(e)),
   #                         self.tr('Processing'), QgsMessageLog.CRITICAL)
   #     return

    def tr(self, string, context=''):
        if context == '':
            context = 'RAlgorithmProvider'
        return QCoreApplication.translate(context, string)
