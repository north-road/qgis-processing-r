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

from typing import List

from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsPointXY)

from processing_r.processing.utils import RUtils


class RTemplates:  # pylint: disable=too-many-public-methods
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
        self._install_github = False
        """
        Variable defining that there are dependencies from github.
        """
        self._github_dependencies = []
        """
        Variable that stores dependencies from github to be installed.
        """
        self._enums_literals = []
        """
        Variable that stores names of literal enums in a list for further processing. The fuction is_literal_enums
        depends directly on this variable.
        """
        self._auto_load_packages = True
        """
        Variable that stores if only file names, not data are passed to the script.
        """

    @property
    def auto_load_packages(self):
        """
        Getter for class variable pass_filenames.
        :return: bool
        """
        return self._auto_load_packages

    @auto_load_packages.setter
    def auto_load_packages(self, value: bool):
        """
        Setter for class variable pass_filenames.
        :param value: bool
        """
        self._auto_load_packages = value

    @property
    def github_dependencies(self):
        """
        Getter for class variable github_dependencies.
        :return: bool
        """
        return self._github_dependencies

    @github_dependencies.setter
    def github_dependencies(self, dependencies: str):
        """
        Setter for class variable github_dependencies.
        :param dependencies: str
        """
        dependencies = dependencies.strip().replace(" ", "").split(",")
        self._github_dependencies = dependencies

    @property
    def install_github(self):
        """
        Getter for class variable install_github.
        :return: bool
        """
        return self._install_github

    @install_github.setter
    def install_github(self, use: bool):
        """
        Setter for class variable install_github.
        :param use: bool
        """
        self._install_github = use

    @property
    def use_sf(self):
        """
        Getter for class variable use_sf.
        :return: bool
        """
        return self._use_sf

    @use_sf.setter
    def use_sf(self, use: bool):
        """
        Setter for class variable use_sf.
        :param use: bool
        """
        self._use_sf = use

    @property
    def use_raster(self):
        """
        Getter fir class variable use_raster.
        :return: bool
        """
        return self._use_raster

    @use_raster.setter
    def use_raster(self, use: bool):
        """
        Setter for class variable use_raster.
        :param use: bool
        """
        self._use_raster = use

    def get_necessary_packages(self) -> list:
        """
        Produces list of necessary packages for the script based on values of variables use_raster and use_sf.

        :return: list of strings with names of packages
        """
        packages = []

        if self.auto_load_packages:
            if self.use_sf:
                packages.append("sf")
            else:
                packages.append("rgdal")
                packages.append("sp")

            if self.use_raster:
                packages.append("raster")
            else:
                packages.append("rgdal")

        if self.install_github:
            packages.append("remotes")

        return packages

    def __set_variable_vector_sf(self, variable: str, path: str, layer: str = None) -> str:
        """
        Internal function that produces R code to read vector data using sf package.

        :param variable: string
        :param path: string
        :param layer: string
        :return: string
        """
        command = ""

        if layer is not None:
            command = '{0} <- st_read("{1}", layer = "{2}", quiet = TRUE, stringsAsFactors = FALSE)'.format(variable,
                                                                                                            path, layer)
        else:
            command = '{0} <- st_read("{1}", quiet = TRUE, stringsAsFactors = FALSE)'.format(variable, path)

        return command

    def __set_variable_vector_rgdal(self, variable: str, path: str, layer: str = None) -> str:
        """
        Internal function that produces R code to read vector data using rgdal package.

        :param variable: string
        :param path: string
        :param layer: string
        :return: string
        """

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
            code = self.__set_variable_vector_sf(variable, path, layer)
        else:
            code = self. __set_variable_vector_rgdal(variable, path, layer)

        return code

    def __set_variable_raster_raster(self, variable: str, path: str) -> str:
        """
        Internal function that produces R code to read raster data using raster package.

        :param variable: string
        :param path: string
        :return: string
        """
        return '{0} <- brick("{1}")'.format(variable, path)

    def __set_variable_raster_gdal(self, variable: str, path: str) -> str:
        """
        Internal function that produces R code to read raster data using rgdal package.

        :param variable: string
        :param path: string
        :return: string
        """

        return '{0} <- readGDAL("{1}")'.format(variable, path)

    def set_variable_raster(self, variable: str, path: str) -> str:
        """
        Function that produces R code to read raster data.

        :param variable: string. Name of the variable.
        :param path: string. Path to read data from.
        :return: string. R code to read raster data.
        """

        if self.use_raster:
            code = self.__set_variable_raster_raster(variable, path)
        else:
            code = self.__set_variable_raster_gdal(variable, path)

        return code

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

        if '"' in value:
            value = value.replace('"', '\\"')

        return '{0} <- "{1}"'.format(variable, value)

    def set_variable_string_list(self, variable: str, value: List[str]) -> str:
        """
        Function that produces R code to specify string list variable.

        :param variable: string. Name of the variable.
        :param value: list of strings. Value of the variable.
        :return: string. R code to produce variable with given value.
        """
        escaped_values = []
        for v in value:
            if '"' in v:
                v = v.replace('"', '\\"')
            escaped_values.append('"{0}"'.format(v))

        return '{0} <- c({1})'.format(variable, ','.join(escaped_values))

    def set_variable_directly(self, variable: str, value) -> str:
        """
        Function that produces R code to specify variable directly.

        :param variable: string. Name of the variable.
        :param value: Value of the variable.
        :return: string. R code to produce variable with given value.
        """
        return '{0} <- {1}'.format(variable, value)

    def set_variable_null(self, variable: str) -> str:
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
        """
        Internal function that produces R code to write vector data using sf package.

        :param variable: string
        :param path: string
        :param layer_name: string
        :return: string
        """

        command = ""

        if layer_name is not None:
            command = 'st_write({0}, "{1}", layer = "{2}", quiet = TRUE)'.format(variable, path, layer_name)
        else:
            command = 'st_write({0}, "{1}", quiet = TRUE)'.format(variable, path)

        return command

    def __write_vector_ogr(self, variable: str, path: str, layer_name: str = None, driver: str = "gpkg") -> str:
        """
        Internal function that produces R code to write vector data using rgdal package.

        :param variable: string
        :param path: string
        :param layer_name: string
        :param driver: string
        :return: string
        """

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
            code = self.__write_vector_sf(variable, path, layer_name)
        else:
            code = self.__write_vector_ogr(variable, path, layer_name, driver)

        return code

    def __write_raster_raster(self, variable: str, path: str) -> str:
        """
        Internal function that produces R code to write raster data using raster package.

        :param variable: string
        :param path: string
        :return: string
        """
        return 'writeRaster({0}, "{1}", overwrite = TRUE)'.format(variable, path)

    def __write_raster_gdal(self, variable: str, path: str) -> str:
        """
        Internal function that produces R code to write raster data using rgdal package.

        :param variable: string
        :param path: string
        :return: stringable_n
        """

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
            code = self.__write_raster_raster(variable, path)
        else:
            code = self.__write_raster_gdal(variable, path)

        return code

    def write_csv_output(self, variable: str, path: str) -> str:
        """
        Functions that produces R code to write table data.

        :param variable: string. Name of the variable to write.
        :param path: string. Path to write the data to.
        :return: string. R code to write table data to disc.
        """
        return 'write.csv({0}, "{1}")'.format(variable, path)

    def install_package_github(self, repo: str) -> str:
        """
        Function that produces R code to install

        :param repo: string. Name of the repo to be installed.
        :return: string. R code to install package from a repo.
        """
        return 'remotes::install_github("{0}")'.format(repo)

    def write_cat_output(self, variable: str, path: str) -> list:
        """
        Functions that produces R code to write variable.

        Values are stred into the file like:
        ##output1_name
        output1_value
        ##output2_name
        output2_value

        :param variable: string. Name of the variable to write.
        :param path: string. Path to write the data to.
        :return: list. R code to write varaible to disc.
        """
        commands = []
        commands.append('cat("##{0}", file="{1}", sep="\n", append=TRUE)'.format(variable, path))
        commands.append('cat({0}, file="{1}", sep="\n", append=TRUE)'.format(variable, path))
        return commands

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
        return '.libPaths(\"{0}\")'.format(path.replace('\\', '/'))

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

    def build_script_header_commands(self, script) -> List[str]:
        """
        Builds the set of script startup commands for the algorithm, based on necessary packages,
        github_install parameter and script analysis.

        :param script: variable self.script from RAlgorithm
        :return: list of str (commands)
        """

        commands = list()

        # Just use main mirror
        commands.append(self.set_option_repos(RUtils.package_repo()))

        # Try to install packages if needed
        if RUtils.use_user_library():
            path_to_use = str(RUtils.r_library_folder()).replace('\\', '/')
            commands.append(self.change_libPath(path_to_use))

        packages = self.get_necessary_packages()

        for p in packages:
            commands.append(self.check_package_availability(p))
            commands.append(self.load_package(p))

        if self.install_github:
            for dependency in self.github_dependencies:
                commands.append(self.install_package_github(dependency))

        packages_script = RUtils.get_required_packages(script)

        for p in packages_script:
            commands.append(self.check_package_availability(p))
            commands.append(self.load_package(p))

        return commands

# set of functions related to enum creation
    def add_literal_enum(self, enum_name: str):
        """
        Functions that registers enum as literal.
        :param enum_name: string. Name of the variable.
        :return:
        """
        self._enums_literals.append(enum_name)

    def set_variable_enum_value(self, enum_name: str, number: int, enum_values: list) -> str:
        """
        Produces R code that creates string variable with selected enum option.
        :param enum_name: string. Name of the variable.
        :param number: integer. Number of selected option from the list (enum_values).
        :param enum_values: list. List of options for the given enum.
        :return: string. R code representing the value from enum as string.
        """
        return self.set_variable_string(enum_name, enum_values[number])

    def is_literal_enum(self, enum_name: str) -> bool:
        """
        Function to check if the given enum is listed as literal.
        :param enum_name: string. Name of the enum variable.
        :return: boolean.
        """
        return enum_name in self._enums_literals

    def set_point(self,
                  variable: str,
                  point: QgsPointXY,
                  crs: QgsCoordinateReferenceSystem) -> list:
        """
        Produces R code that creates a variable from point input.

        :param variable: string. Name of the variable.
        :param point: QgsPointXY. Point to extract x and y coordinates from.
        :param crs: QgsCoordinateReferenceSystem. Coordinate reference system for the point.
        :return: string. R code that constructs the point.
        """

        commands = []

        if self.use_sf:

            commands.append('point_crs <- st_crs(\'{}\')'.format(crs.toWkt()))
            commands.append('{0} <- st_sfc(st_point(c({1},{2})), crs = point_crs)'.format(variable,
                                                                                          point.x(),
                                                                                          point.y()))

        else:

            commands.append('xy_df <- cbind(c({}), c({}))'.format(point.x(),
                                                                  point.y()))
            commands.append('point_crs <- CRS(\'{}\')'.format(crs.toProj4()))
            commands.append('{} <- SpatialPoints(xy_df, proj4string = point_crs)'.format(variable))

        return commands
