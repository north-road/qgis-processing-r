# -*- coding: utf-8 -*-

"""
***************************************************************************
    create_new_script.py
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

from qgis.PyQt.QtCore import QCoreApplication
from processing.gui.ToolboxAction import ToolboxAction
from processing_r.gui.script_editor.script_editor_dialog import ScriptEditorDialog


class CreateNewScriptAction(ToolboxAction):
    """
    Action for creating a new R script
    """

    def __init__(self):
        super().__init__()
        self.name = QCoreApplication.translate("RAlgorithmProvider", "Create New R Script…")
        self.group = self.tr("Tools")

    def execute(self):
        """
        Called whenever the action is triggered
        """
        dlg = ScriptEditorDialog(None)
        dlg.show()
