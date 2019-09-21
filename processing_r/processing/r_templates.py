class RTemplates:

    def __init__(self):
        self._use_sf = True
        self._use_raster = True

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

    def get_necessary_packages(self):
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

    def __set_variable_vector_sf(self, variable: str, path: str, layer: str = None):

        command = ""

        if layer is not None:
            command = '{0} <- st_read("{1}", layer = "{2}", quiet = TRUE, stringsAsFactors = FALSE)'.format(variable,
                                                                                                            path, layer)
        else:
            command = '{0} <- st_read("{1}", quiet = TRUE, stringsAsFactors = FALSE)'.format(variable, path)

        return command

    def __set_variable_vector_rgdal(self, variable: str, path: str, layer: str = None):

        command = ""

        if layer is not None:
            command = '{0}=readOGR("{1}", layer="{2}")'.format(variable, path, layer)
        else:
            command = '{0}=readOGR("{1}")'.format(variable, path)

        return command

    def set_variable_vector(self, variable: str, path: str, layer: str = None):

        if self.use_sf:
            return self.__set_variable_vector_sf(variable, path, layer)
        else:
            return self. __set_variable_vector_rgdal(variable, path, layer)

    def __set_variable_raster_raster(self, variable: str, path: str):
        return '{0} <- brick("{1}")'.format(variable, path)

    def __set_variable_raster_gdal(self, variable: str, path: str):
        return '{0} <- readGDAL("{1}")'.format(variable, path)

    def set_variable_raster(self, variable: str, path: str):

        if self.use_raster:
            return self.__set_variable_raster_raster(variable, path)
        else:
            return self.__set_variable_raster_gdal(variable, path)

    def set_variable_extent(self, variable: str, x_min: float, x_max: float, y_min: float, y_max: float):
        return '{0} <- extent({1},{2},{3},{4})'.format(variable, x_min, x_max, y_min, y_max)

    def set_variable_string(self, variable: str, value: str):
        return '{0} <- "{1}"'.format(variable, value)

    def set_variable_directly(self, variable: str, value):
        return '{0} <- {1}'.format(variable, value)

    def set_variable_null(self, variable:str):
        return "{0} <- NULL".format(variable)

    def png(self, path: str):
        return 'png("{0}")'.format(path)

    def dev_off(self):
        return 'dev.off()'

    def __write_vector_sf(self, variable: str, path: str, layer_name: str = None):

        command = ""

        if layer_name is not None:
            command = 'st_write({0}, "{1}", layer = "{2}", quiet = TRUE)'.format(variable, path, layer_name)
        else:
            command = 'st_write({0}, "{1}", quiet = TRUE)'.format(variable, path)

        return command

    def __write_vector_ogr(self, variable: str, path: str, layer_name: str = None, driver: str = "gpkg"):

        command = 'writeOGR({0},"{1}","{2}", driver="{3}")'.format(variable, path, layer_name, driver)

        return command

    def write_vector_output(self, variable: str, path: str, layer_name: str = None, driver: str = "gpkg"):

        if self.use_sf:
            return self.__write_vector_sf(variable, path, layer_name)
        else:
            return self.__write_vector_ogr(variable, path, layer_name, driver)

    def __write_raster_raster(self, variable: str, path: str):
        return 'writeRaster({0}, "{1}", overwrite = TRUE)'.format(variable, path)

    def __write_raster_gdal(self, variable: str, path: str):
        if not path.lower().endswith('tif'):
            path = path + '.tif'
        return 'writeGDAL({0}, "{1}")'.format(variable, path)

    def write_raster_output(self, variable: str, path: str):

        if self.use_raster:
            return self.__write_raster_raster(variable, path)
        else:
            return self.__write_raster_gdal(variable, path)

    def write_csv_output(self, variable: str, path: str):
        return 'write.csv({0}, "{1}")'.format(variable, path)

    def check_package_availability(self, package_name: str):

        command = 'tryCatch(find.package("{0}"), error = function(e) install.packages("{0}", dependencies=TRUE))'\
            .format(package_name)

        return command

    def load_package(self, package_name: str):
        return 'library("{0}")'.format(package_name)

    def change_libPath(self, path: str):
        return '.libPaths({0})'.format(path)

    def set_option(self, option_name: str, value: str):
        return 'options("{0}"="{1}")'.format(option_name, value)

    def set_option_repos(self, value: str):
        return self.set_option("repos", value)
