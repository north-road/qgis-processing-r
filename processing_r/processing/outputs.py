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

from qgis.core import (QgsProcessing,
                       QgsProcessingOutputRasterLayer,
                       QgsProcessingOutputVectorLayer,
                       QgsProcessingOutputMapLayer,
                       QgsProcessingOutputHtml,
                       QgsProcessingOutputNumber,
                       QgsProcessingOutputString,
                       QgsProcessingOutputFolder,
                       QgsProcessingOutputFile,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterFileDestination)


def create_output_from_string(s: str):
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
        if tokens[1].lower().strip()[:len('output')] != 'output':
            return None

        name = tokens[0]
        description = tokens[0]

        token = tokens[1].strip()[len('output') + 1:]
        return create_output_from_token(name, description, token)

    except IndexError:
        return None


OUTPUT_FACTORY = {
    'layer': QgsProcessingOutputMapLayer,
    'folder': QgsProcessingOutputFolder,
    'file': QgsProcessingOutputFile,
    'html': QgsProcessingOutputHtml,
    'number': QgsProcessingOutputNumber,
    'string': QgsProcessingOutputString,
    'raster': QgsProcessingOutputRasterLayer
}


def create_output_from_token(name: str, description: str, token: str):  # pylint: disable=too-many-branches
    """
    Creates an output (or destination parameter) definition from a token string
    """
    no_prompt = False
    if 'noprompt' in token:
        no_prompt = True
        token = token.replace(' noprompt', '')

    output_type = token.lower().strip()

    out = None
    if output_type.startswith('vector'):
        vector_type = QgsProcessing.TypeVectorAnyGeometry
        if output_type == 'vector point':
            vector_type = QgsProcessing.TypeVectorPoint
        elif output_type == 'vector line':
            vector_type = QgsProcessing.TypeVectorLine
        elif output_type == 'vector polygon':
            vector_type = QgsProcessing.TypeVectorPolygon
        if no_prompt:
            out = QgsProcessingOutputVectorLayer(name, description, vector_type)
        else:
            out = QgsProcessingParameterVectorDestination(name, description, type=vector_type)
    elif output_type.startswith('table'):
        if no_prompt:
            out = QgsProcessingOutputVectorLayer(name, description, QgsProcessing.TypeVector)
        else:
            out = QgsProcessingParameterVectorDestination(name, description, type=QgsProcessing.TypeVector)
    elif output_type == 'multilayers':
        # out = QgsProcessingOutputMultipleLayers(name, description)
        #            elif token.lower().strip() == 'vector point':
        #                out = OutputVector(datatype=[dataobjects.TYPE_VECTOR_POINT])
        #            elif token.lower().strip() == 'vector line':
        #                out = OutputVector(datatype=[OutputVector.TYPE_VECTOR_LINE])
        #            elif token.lower().strip() == 'vector polygon':
        #                out = OutputVector(datatype=[OutputVector.TYPE_VECTOR_POLYGON])
        #            elif token.lower().strip().startswith('table'):
        #                out = OutputTable()
        #            elif token.lower().strip().startswith('file'):
        #                out = OutputFile()
        #                ext = token.strip()[len('file') + 1:]
        #                if ext:
        #                    out.ext = ext
        #            elif token.lower().strip().startswith('extent'):
        #                out = OutputExtent()
        pass
    elif not no_prompt:
        if output_type.startswith('raster'):
            out = QgsProcessingParameterRasterDestination(name, description)
        elif output_type.startswith('folder'):
            out = QgsProcessingParameterFolderDestination(name, description)
        elif output_type.startswith('html'):
            out = QgsProcessingParameterFileDestination(name, description, 'HTML Files (*.html)')
        elif output_type.startswith('file'):
            ext = token.strip()[len('file') + 1:]
            if ext:
                out = QgsProcessingParameterFileDestination(name, description, '%s Files (*.%s)' % (ext.upper(), ext))
            else:
                out = QgsProcessingParameterFileDestination(name, description)
    if not out and output_type in OUTPUT_FACTORY:
        return OUTPUT_FACTORY[output_type](name, description)
    if not out and output_type.startswith('file'):
        return OUTPUT_FACTORY['file'](name, description)

    return out
