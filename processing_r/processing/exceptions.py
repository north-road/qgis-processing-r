# -*- coding: utf-8 -*-

"""
***************************************************************************
    exceptions.py
    ---------------------
    Date                 : November 2018
    Copyright            : (C) 2018 by Nyall Dawson
    Email                : nyall dot dawson at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""


class InvalidScriptException(Exception):
    """
    Raised on encountering an invalid script
    """

    def __init__(self, msg):
        super().__init__()
        self.msg = msg
