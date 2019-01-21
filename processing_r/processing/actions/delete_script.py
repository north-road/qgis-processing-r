# -*- coding: utf-8 -*-

"""
***************************************************************************
    delete_script.py
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

import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsApplication, QgsProcessingAlgorithm
from processing.gui.ContextAction import ContextAction


class DeleteScriptAction(ContextAction):
    """
    Toolbox context menu action for deleting an existing script
    """

    def __init__(self):
        super().__init__()
        self.name = QCoreApplication.translate("DeleteScriptAction", "Delete Script…")

    def isEnabled(self):
        """
         Returns whether the action is enabled
         """
        return isinstance(self.itemData, QgsProcessingAlgorithm) and self.itemData.provider().id() == "r" and self.itemData.is_user_script

    def execute(self):
        """
        Called whenever the action is triggered
        """
        reply = QMessageBox.question(None,
                                     self.tr("Delete Script"),
                                     self.tr("Are you sure you want to delete this script?"),
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            file_path = self.itemData.description_file
            if file_path is not None:
                os.remove(file_path)
                QgsApplication.processingRegistry().providerById("r").refreshAlgorithms()
            else:
                QMessageBox.warning(None,
                                    self.tr("Delete Script"),
                                    self.tr("Can not find corresponding script file."))
