# Changelog

- 2.3.0 Introduces support for QgsProcessingParameterPoint as an input variable, set parameter help strings under QGIS 3.16 or later

- 2.2.2 Make sure that FolderDestination and FileDestination folders exist, otherwise that would have to be handled by R script
  causes issue if writing to temp directory which does not exist

- 2.2.1 Fix file based outputs, R version number reporting

- 2.2.0 Add support for file based outputs.

- 2.1.0 Added support for literal enums, skipping package loading, additional output types (e.g. strings and numbers).

- 2.0.0 Many fixes, algorithms have support for choice between sf/raster or rgdal for loading inputs

- 1.0.7 Fix 3.4 compatibility

- 1.0.6 Workaround API break in QGIS, which breaks existing scripts

- 1.0.5 Allow use of R development versions

- 1.0.4 Resurrect ability to run on selected features only

- 1.0.3 Remove activation setting for provider (disable plugin instead!), fix memory layer handling, simpler example script

- 1.0.2 Fix vector paths under windows