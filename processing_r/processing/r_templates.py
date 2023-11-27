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

from typing import List, Any, Tuple, Optional

from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsPointXY,
                       QgsGeometry)

from qgis.PyQt.QtCore import QDateTime, Qt, QDate, QTime

from qgis.PyQt.QtGui import QColor

from processing_r.processing.utils import RUtils


class RTemplates:  # pylint: disable=too-many-public-methods
    """
    Class for generating R code
    """

    def __init__(self):
        self._use_lubridate = False
        """
        Variable specifying whether lubridate package should be used.
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
        self.expressions = []
        """
        Variable that stores header lines with QGIS expressions
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

    def get_necessary_packages(self) -> list:
        """
        Produces list of necessary packages for the script.

        :return: list of strings with names of packages
        """
        packages = []

        if self.auto_load_packages:
            packages.append("sf")
            packages.append("raster")

        if self._use_lubridate:
            packages.append("lubridate")

        if self.install_github:
            packages.append("remotes")

        return packages

    def set_variable_vector(self, variable: str, path: str, layer: str = None) -> str:
        """
        Function that produces R code to read vector data.

        :param variable: string. Name of the variable.
        :param path: string. Path to read data from.
        :param layer: string. Name of the layer, if necessary.
        :return: string. R code to read vector data.
        """

        if layer is not None:
            command = '{0} <- st_read("{1}", layer = "{2}", quiet = TRUE, stringsAsFactors = FALSE)'.format(variable,
                                                                                                            path, layer)
        else:
            command = '{0} <- st_read("{1}", quiet = TRUE, stringsAsFactors = FALSE)'.format(variable, path)

        return command

    def set_variable_raster(self, variable: str, path: str) -> str:
        """
        Function that produces R code to read raster data.

        :param variable: string. Name of the variable.
        :param path: string. Path to read data from.
        :return: string. R code to read raster data.
        """

        return '{0} <- brick("{1}")'.format(variable, path)

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

        return '{0} <- {1}'.format(variable, self._r_string(value))

    def _r_string(self, value: str) -> str:
        """
        Generate R string.
        """

        if '"' in value:
            value = value.replace('"', '\\"')

        return '"{}"'.format(value)

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

    def set_variable_geom(self, variable: str, geom_wkt_value: str) -> str:
        """
        Create sfg from WKT.

        :param variable: string. Name of the variable.
        :param geom_wkt_value: string. WKT of geometry.
        :return: string. R code to creating variable of classes sfg.
        """
        return '{0} <- {1}'.format(variable, self._r_geom(geom_wkt_value))

    def _r_geom(self, geom_wkt_value: str) -> str:
        """
        Generate R string.
        """

        return 'sf::st_as_sfc("{}")[[1]]'.format(geom_wkt_value)

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

    def write_vector_output(self, variable: str, path: str, layer_name: str = None) -> str:
        """
        Functions that produces R code to write vector data.

        :param variable: string. Name of the variable to write.
        :param path: string. Path to write the data to.
        :param layer_name: string. Name of the layer if necessary.
        :param driver: string. GDAL driver name to use. Default value "GPKG" - geopackage.
        :return: string. R code to write vector data to disc.
        """
        if layer_name is not None:
            command = 'st_write({0}, "{1}", layer = "{2}", quiet = TRUE)'.format(variable, path, layer_name)
        else:
            command = 'st_write({0}, "{1}", quiet = TRUE)'.format(variable, path)

        return command

    def write_raster_output(self, variable: str, path: str) -> str:
        """
        Functions that produces R code to write raster data.

        :param variable: string. Name of the variable to write.
        :param path: string. Path to write the data to.
        :return: string. R code to write raster data to disc.
        """
        return 'writeRaster({0}, "{1}", overwrite = TRUE)'.format(variable, path)

    def write_csv_output(self, variable: str, path: str) -> str:
        """
        Functions that produces R code to write table data.

        :param variable: string. Name of the variable to write.
        :param path: string. Path to write the data to.
        :return: string. R code to write table data to disc.
        """
        return 'write.csv({0}, "{1}", row.names = FALSE)'.format(variable, path)

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

    def extract_package_name_options(self, package_load_string: str) -> Tuple[str, Optional[str]]:
        """
        Returns package name and options if they exist.
        """

        if "," in package_load_string:

            splitted = package_load_string.split(",", maxsplit=1)

            package_name = splitted[0]
            load_options = splitted[1]

        else:

            package_name = package_load_string
            load_options = None

        return package_name, load_options

    def check_package_availability(self, package_name: str) -> str:
        """
        Function that produces R code to check availability and install missing R packages.

        :param package_name: string. Name of the package to check.
        :return: string. R code to check the package and install it if missing.
        """

        package, _ = self.extract_package_name_options(package_name)

        command = 'tryCatch(find.package("{0}"), error = function(e) install.packages("{0}", dependencies=TRUE))' \
            .format(package)

        return command

    def load_package(self, package_name: str) -> str:
        """
        Function that produces R code to load package.

        :param package_name: string. Name of the package.
        :return: string. R code to load given package.
        """

        package, options = self.extract_package_name_options(package_name)

        if options:
            library_command = 'library("{0}",{1})'.format(package, options)
        else:
            library_command = 'library("{0}")'.format(package_name)

        return library_command

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

        commands = []

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

        commands.append('point_crs <- st_crs(\'{}\')'.format(crs.toWkt()))
        commands.append('{0} <- st_sfc(st_point(c({1},{2})), crs = point_crs)'.format(variable,
                                                                                      point.x(),
                                                                                      point.y()))

        return commands

    def set_range(self,
                  variable: str,
                  rgn: list) -> list:
        """
        Produces R code that creates a variable from range input.

        :param variable: string. Name of the variable.
        :param rgn: QgsDoubleRange. list of values min-max.
        :return: string. R code that constructs the vector.
        """

        commands = []
        commands.append('{0} <- c(min = {1}, max = {2})'.format(variable, rgn[0], rgn[1]))

        return commands

    def set_color(self,
                  variable: str,
                  color: QColor) -> list:
        """
        Produces R code that creates a variable from color input.

        :param variable: string. Name of the variable.
        :param color: QColor. Red, green, blue and alpha values.
        :return: string. R code that constructs the color hex string.
        """

        commands = []
        commands.append('{0} <- rgb({1}, {2}, {3}, {4}, maxColorValue = 255)'.format(variable,
                                                                                     color.red(),
                                                                                     color.green(),
                                                                                     color.blue(),
                                                                                     color.alpha()))

        return commands

    def _r_color(self, color: QColor) -> str:
        """
        Generate R string.
        """

        return 'rgb({0}, {1}, {2}, {3}, maxColorValue = 255)'.format(color.red(),
                                                                     color.green(),
                                                                     color.blue(),
                                                                     color.alpha())

    def set_datetime(self,
                     variable: str,
                     datetime: QDateTime) -> list:
        """
        Produces R code that creates a variable from datetime input.

        :param variable: string. Name of the variable.
        :param datetime: QDateTime. Red, green, blue and alpha values.
        :return: string. R code that constructs the color hex string.
        """
        dtt = datetime.toString(format=Qt.ISODate)
        commands = []
        commands.append('{0} <- as.POSIXct("{1}", format = "%Y-%m-%dT%H:%M:%S")'.format(variable, dtt))

        return commands

    def _r_datetime(self, datetime: QDateTime) -> str:
        """
        Generate R string.
        """

        datetime = datetime.toString(format=Qt.ISODate)

        return 'as.POSIXct("{}", format = "%Y-%m-%dT%H:%M:%S")'.format(datetime)

    def set_date(self,
                 variable: str,
                 date: QDate) -> str:
        """
        Produces R code that creates a variable from date input.

        :param variable: string. Name of the variable.
        :param date: QDate.
        :return: string. R code that constructs the date.
        """

        return '{0} <- {1}'.format(variable, self._r_date(date))

    def _r_date(self, date: QDate) -> str:
        """
        Generate R string.
        """

        date = date.toString(format=Qt.ISODate)

        return 'as.POSIXct("{}", format = "%Y-%m-%d")'.format(date)

    def set_time(self,
                 variable: str,
                 time: QTime) -> str:
        """
        Produces R code that creates a variable from time input.

        :param variable: string. Name of the variable.
        :param time: QTime
        :return: string. R code that constructs the time.
        """

        return '{0} <- {1}'.format(variable, self._r_time(time))

    def _r_time(self, time: QTime) -> str:
        """
        Generate R string.
        """

        self._use_lubridate = True

        return 'lubridate::hms("{}")'.format(time.toString(Qt.TextDate))

    def set_variable_list(self,
                          variable: str,
                          values_list: List[Any]) -> Any:
        """
        Generate R code for list of values.

        :param variable: string. Name of the variable.
        :param values_list: List[Any]. List of expression values.
        :return: string. R code that constructs the list objects.
        """
        values = []

        for value in values_list:

            if isinstance(value, str):

                values.append(self._r_string(value))

            elif isinstance(value, (int, float)):

                values.append('{}'.format(value))

            elif isinstance(value, QDateTime):

                values.append(self._r_datetime(value))

            elif isinstance(value, QDate):

                values.append(self._r_date(value))

            elif isinstance(value, QTime):

                values.append(self._r_time(value))

            elif isinstance(value, QgsGeometry):

                values.append(self._r_geom(value.asWkt()))

            elif isinstance(value, QColor):

                values.append(self._r_color(value))

        return '{0} <- list({1})'.format(variable, ", ".join(values))
