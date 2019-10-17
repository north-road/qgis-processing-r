# -*- coding: utf-8 -*-
"""Class for producing R code

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = '(C) 2019 by Jan Caha'
__date__ = '17/10/2019'
__copyright__ = 'Copyright 2018, North Road'


class RTemplates:
    """
    Class for generating R code
    """

    def __init__(self):
        self._use_sf = True
        """
        Variable defining that vectors will be read through package `sf` if `TRUE` or through `rgdal` and `sp` if
        `FALSE`.
        """
        self._use_raster = True
        """
        Variable defining that rasters will be read through package `raster` if `TRUE` or through `rgdal` and `sp` if
        `FALSE`.
        """

    @property
    def use_sf(self):
        return self._use_sf

    @use_sf.setter
    def use_sf(self, use: bool):
        self._use_sf = use

    @property
    def use_raster(self):
        return self._use_raster

    @use_raster.setter
    def use_raster(self, use: bool):
        self._use_raster = use

    def get_necessary_packages(self) -> list:
        """
        Produces list of necessary packages for the script based on values of variables use_raster and use_sf.

        :return: list of strings with names of packages
        """
        packages = []

        if self.use_sf:
            packages.append("sf")
        else:
            packages.append("rgdal")
            packages.append("sp")

        if self.use_raster:
            packages.append("raster")
        else:
            packages.append("rgdal")

        return packages

    def __set_variable_vector_sf(self, variable: str, path: str, layer: str = None) -> str:
        command = ""

        if layer is not None:
            command = '{0} <- st_read("{1}", layer = "{2}", quiet = TRUE, stringsAsFactors = FALSE)'.format(variable,
                                                                                                            path, layer)
        else:
            command = '{0} <- st_read("{1}", quiet = TRUE, stringsAsFactors = FALSE)'.format(variable, path)

        return command

    def __set_variable_vector_rgdal(self, variable: str, path: str, layer: str = None) -> str:

        command = ""

        if layer is not None:
            command = '{0} <- readOGR("{1}", layer="{2}")'.format(variable, path, layer)
        else:
            command = '{0} <- readOGR("{1}")'.format(variable, path)

        return command

    def set_variable_vector(self, variable: str, path: str, layer: str = None) -> str:
        """
        Function that produces R code to read vector data.

        :param variable: string. Name of the variable.
        :param path: string. Path to read data from.
        :param layer: string. Name of the layer, if necessary.
        :return: string. R code to read vector data.
        """

        if self.use_sf:
            return self.__set_variable_vector_sf(variable, path, layer)
        else:
            return self. __set_variable_vector_rgdal(variable, path, layer)

    def __set_variable_raster_raster(self, variable: str, path: str) -> str:
        return '{0} <- brick("{1}")'.format(variable, path)

    def __set_variable_raster_gdal(self, variable: str, path: str) -> str:
        return '{0} <- readGDAL("{1}")'.format(variable, path)

    def set_variable_raster(self, variable: str, path: str) -> str:
        """
        Function that produces R code to read raster data.

        :param variable: string. Name of the variable.
        :param path: string. Path to read data from.
        :return: string. R code to read raster data.
        """

        if self.use_raster:
            return self.__set_variable_raster_raster(variable, path)
        else:
            return self.__set_variable_raster_gdal(variable, path)

    def set_variable_extent(self, variable: str, x_min: float, x_max: float, y_min: float, y_max: float):
        """
        Function that produces R code to specify spatial extent.

        :param variable: string. Name of the variable.
        :param x_min: float. Minimal x coordinate.
        :param x_max: float. Maximal x coordinate.
        :param y_min: float. Minimal y coordinate.
        :param y_max: float. Maximal y coordinate.
        :return: string. R code to produce extent variable.
        """
        return '{0} <- extent({1},{2},{3},{4})'.format(variable, x_min, x_max, y_min, y_max)

    def set_variable_string(self, variable: str, value: str) -> str:
        """
        Function that produces R code to specify string variable.

        :param variable: string. Name of the variable.
        :param value: string. Value of the variable.
        :return: string. R code to produce variable with given value.
        """
        return '{0} <- "{1}"'.format(variable, value)

    def set_variable_directly(self, variable: str, value) -> str:
        """
        Function that produces R code to specify variable directly.

        :param variable: string. Name of the variable.
        :param value: Value of the variable.
        :return: string. R code to produce variable with given value.
        """
        return '{0} <- {1}'.format(variable, value)

    def set_variable_null(self, variable:str) -> str:
        """
        Function that produces R code to specify variable with `NULL` value.

        :param variable: string. Name of the variable.
        :return: string. R code to produce variable with `NULL` value.
        """
        return "{0} <- NULL".format(variable)

    def create_png(self, path: str) -> str:
        """
        Funtion that produces R code to write PNG file at given location.

        :param path: string. Path to save PNG to.
        :return: string. R code to save PNG file.
        """
        return 'png("{0}")'.format(path)

    def dev_off(self) -> str:
        """
        Function that produces R code which closes and finalizes graphical output.

        :return: string. R code to close graphical device.
        """
        return 'dev.off()'

    def __write_vector_sf(self, variable: str, path: str, layer_name: str = None) -> str:

        command = ""

        if layer_name is not None:
            command = 'st_write({0}, "{1}", layer = "{2}", quiet = TRUE)'.format(variable, path, layer_name)
        else:
            command = 'st_write({0}, "{1}", quiet = TRUE)'.format(variable, path)

        return command

    def __write_vector_ogr(self, variable: str, path: str, layer_name: str = None, driver: str = "gpkg") -> str:

        command = 'writeOGR({0}, "{1}", "{2}", driver="{3}")'.format(variable, path, layer_name, driver)

        return command

    def write_vector_output(self, variable: str, path: str, layer_name: str = None, driver: str = "gpkg") -> str:
        """
        Functions that produces R code to write vector data.

        :param variable: string. Name of the variable to write.
        :param path: string. Path to write the data to.
        :param layer_name: string. Name of the layer if necessary.
        :param driver: string. GDAL driver name to use. Default value "GPKG" - geopackage.
        :return: string. R code to write vector data to disc.
        """
        if self.use_sf:
            return self.__write_vector_sf(variable, path, layer_name)
        else:
            return self.__write_vector_ogr(variable, path, layer_name, driver)

    def __write_raster_raster(self, variable: str, path: str) -> str:
        return 'writeRaster({0}, "{1}", overwrite = TRUE)'.format(variable, path)

    def __write_raster_gdal(self, variable: str, path: str) -> str:
        if not path.lower().endswith('tif'):
            path = path + '.tif'
        return 'writeGDAL({0}, "{1}")'.format(variable, path)

    def write_raster_output(self, variable: str, path: str) -> str:
        """
        Functions that produces R code to write raster data.

        :param variable: string. Name of the variable to write.
        :param path: string. Path to write the data to.
        :return: string. R code to write raster data to disc.
        """
        if self.use_raster:
            return self.__write_raster_raster(variable, path)
        else:
            return self.__write_raster_gdal(variable, path)

    def write_csv_output(self, variable: str, path: str) -> str:
        """
        Functions that produces R code to write table data.

        :param variable: string. Name of the variable to write.
        :param path: string. Path to write the data to.
        :return: string. R code to write table data to disc.
        """
        return 'write.csv({0}, "{1}")'.format(variable, path)

    def check_package_availability(self, package_name: str) -> str:
        """
        Function that produces R code to check availability and install missing R packages.

        :param package_name: string. Name of the package to check.
        :return: string. R code to check the package and install it if missing.
        """
        command = 'tryCatch(find.package("{0}"), error = function(e) install.packages("{0}", dependencies=TRUE))'\
            .format(package_name)

        return command

    def load_package(self, package_name: str) -> str:
        """
        Function that produces R code to load package.

        :param package_name: string. Name of the package.
        :return: string. R code to load given package.
        """
        return 'library("{0}")'.format(package_name)

    def change_libPath(self, path: str) -> str:
        """
        Function that produces R code to change path where R packages are searched for and installed.

        :param path: string. Path to search for packages and install there if missing.
        :return: string. R code to change path to package library.
        """
        return '.libPaths({0})'.format(path)

    def set_option(self, option_name: str, value: str) -> str:
        """
        Function that produces R code to set R option.

        :param option_name: string. Name of the option to set.
        :param value: string. Value to set the option to.
        :return: string. R code to set option to given value.
        """
        return 'options("{0}"="{1}")'.format(option_name, value)

    def set_option_repos(self, value: str) -> str:
        """
        Function that produces R code to set R option repos to given location.

        :param value: string. Location of the repos to use.
        :return: string. R code to set repos to given value.
        """
        return self.set_option("repos", value)
