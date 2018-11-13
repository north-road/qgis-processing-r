# -*- coding: utf-8 -*-

"""
***************************************************************************
    Output.py
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

import sys

from qgis.core import (QgsProcessingOutputRasterLayer,
                       QgsProcessingOutputVectorLayer,
                       QgsProcessingOutputMapLayer,
                       QgsProcessingOutputHtml,
                       QgsProcessingOutputNumber,
                       QgsProcessingOutputString,
                       QgsProcessingOutputFolder,
                       QgsProcessingOutputMultipleLayers)


def create_output_from_string(s):
    """
    Tries to create an algorithm output from a line string
    """
    try:
        if "|" in s and s.startswith("Output"):
            tokens = s.split("|")
            params = [t if str(t) != "None" else None for t in tokens[1:]]
            clazz = getattr(sys.modules[__name__], tokens[0])
            return clazz(*params)

        tokens = s.split("=")
        if not tokens[1].lower()[:len('output')] == 'output':
            return None

        name = tokens[0]
        description = tokens[0]

        token = tokens[1].strip()[len('output') + 1:]
        out = None

        if token.lower().strip().startswith('raster'):
            out = QgsProcessingOutputRasterLayer(name, description)
        elif token.lower().strip() == 'vector':
            out = QgsProcessingOutputVectorLayer(name, description)
        elif token.lower().strip() == 'layer':
            out = QgsProcessingOutputMapLayer(name, description)
        elif token.lower().strip() == 'multilayers':
            out = QgsProcessingOutputMultipleLayers(name, description)
#            elif token.lower().strip() == 'vector point':
#                out = OutputVector(datatype=[dataobjects.TYPE_VECTOR_POINT])
#            elif token.lower().strip() == 'vector line':
#                out = OutputVector(datatype=[OutputVector.TYPE_VECTOR_LINE])
#            elif token.lower().strip() == 'vector polygon':
#                out = OutputVector(datatype=[OutputVector.TYPE_VECTOR_POLYGON])
#            elif token.lower().strip().startswith('table'):
#                out = OutputTable()
        elif token.lower().strip().startswith('html'):
            out = QgsProcessingOutputHtml(name, description)
#            elif token.lower().strip().startswith('file'):
#                out = OutputFile()
#                ext = token.strip()[len('file') + 1:]
#                if ext:
#                    out.ext = ext
        elif token.lower().strip().startswith('folder'):
            out = QgsProcessingOutputFolder(name, description)
        elif token.lower().strip().startswith('number'):
            out = QgsProcessingOutputNumber(name, description)
        elif token.lower().strip().startswith('string'):
            out = QgsProcessingOutputString(name, description)
#            elif token.lower().strip().startswith('extent'):
#                out = OutputExtent()

        return out
    except IndexError:
        return None
