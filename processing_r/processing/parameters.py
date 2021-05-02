# -*- coding: utf-8 -*-

"""
***************************************************************************
    parameters.py
    ---------------------
    Date                 : April 2021
    Copyright            : (C) 2021 by René-Luc Dhont
    Email                : rldhont at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from processing.core.parameters import getParameterFromString

from processing_r.processing.utils import RUtils


def create_parameter_from_string(s: str):
    """
    Tries to create an algorithm parameter from a line string
    """
    if "|" in s and s.startswith("##QgsProcessingParameter"):
        s = s[2:]
    else:
        s = RUtils.upgrade_parameter_line(s)

        # this is necessary to remove the otherwise unknown keyword
        s = s.replace("enum literal", "enum")

    # this is annoying, but required to work around a bug in early 3.8.0 versions
    try:
        param = getParameterFromString(s, context="")
    except TypeError:
        param = getParameterFromString(s)

    return param
