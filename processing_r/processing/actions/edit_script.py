# -*- coding: utf-8 -*-

"""
***************************************************************************
    edit_script.py
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

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import QgsProcessingAlgorithm
from qgis.utils import iface
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QMessageBox
from processing.gui.ContextAction import ContextAction
from processing_r.gui.script_editor.script_editor_dialog import ScriptEditorDialog


class EditScriptAction(ContextAction):
    """
    Toolbox context menu action for editing an existing script
    """

    def __init__(self):
        super().__init__()
        self.name = QCoreApplication.translate("EditScriptAction", "Edit Script…")

    def isEnabled(self):
        """
         Returns whether the action is enabled
         """
        return isinstance(self.itemData, QgsProcessingAlgorithm) and self.itemData.provider().id() == "r" and self.itemData.is_user_script

    def execute(self):
        """
        Called whenever the action is triggered
        """
        file_path = self.itemData.description_file
        if file_path is not None:
            dlg = ScriptEditorDialog(file_path, iface.mainWindow())
            dlg.show()
        else:
            QMessageBox.warning(None,
                                self.tr("Edit Script"),
                                self.tr("Can not find corresponding script file."))
