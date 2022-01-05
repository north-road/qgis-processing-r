# Script syntax

The R scripts for the plugin use extension **.rsx**. These are classic R scripts with several metadata lines (starting with `##`) that define the interaction between QGIS and R. Metadata amongst other things specify how UI of the tool will look like.

The script loads necessary packages by itself. Combination of _sp_ and _rgdal_ or _sf_ for vector data and _sp_ and _rgdal_ or _raster_ for raster data. Any other packages need to be directly loaded using `library()` command in the script body.

## Metadata

The R script's file name is used to define the script name and id in the R processing provider. You can override these
default metadata with these lines.

`##script_name=name` _script_name_ is the name of the script; under this name, it will be listed in processing toolbox.
It is also used to define the script id in the R processing provider.

`##script_title=display_name` _script_title_ is the title of the script; under this title, it will be listed in processing toolbox.
It overrides the _name_ if it is defined after.

`##group_name=group` _group_name_ is the name of the group of the script, which allows sorting of scripts into groups in processing toolbox.

### Script behaviour

Several metadata lines define the general behaviour of the script.

`##output_plots_to_html` (older version of this metadata keyword is `##showplots`) defines that there will be graphical output from the script that will be presented as an HTML page with images.

`##load_raster_using_rgdal` (legacy alias `##dontuserasterpackage`) specifies that raster data should not be pased to R using [raster](https://CRAN.R-project.org/package=raster) package as **RasterLayer** or **RasterBrick** object. Raster data are instead read using [rgdal](https://CRAN.R-project.org/package=rgdal) into object **SpatialGridDataFrame** from [sp](https://CRAN.R-project.org/package=sp).

`##load_vector_using_rgdal` specifies that vector data should not be pased to R using [sf](https://CRAN.R-project.org/package=sf) package as **sf** **data.frame**. Instead data are passed as **Spatial?DataFrame** (where **?** is the type of vector object) from [sp](https://CRAN.R-project.org/package=sp) package.

`##pass_filenames` (legacy alias `##passfilenames`) specifies that data are not passed directly. Instead only their file names are passed.

`##dont_load_any_packages` specifies that no packages, besides what is directly specified in script, should be loaded. This means that neither of **sf**, **raster**, **sp** or **rgdal** packages is loaded automatically. If spatial data (either raster or vector) should be passed to this script, the metadata `##pass_filenames` should be used as well.

`##user1/repo1,user2/repo2=github_install` allows instalation of **R packages** from GitHub using [remotes](https://CRAN.R-project.org/package=remotes). Multiple repos can be specified and divided by coma, white spaces around are stripped. The formats for repository specification are listed on [remotes website](https://remotes.r-lib.org/#usage).

### Inputs

#### Simple specification

The inputs to R script are specified as: `variable_name=variable_type [default_value/from_variable]`. This metadata line also specifies how tool UI will look in QGIS, as inputs are one section of the tool UI. In this specification _variable_name_ is the name of the variable used in R script, _variable_type_ is a type of input variable from possible input types (vector, raster, table, number, string, boolean, Field).
This metadata line is based on the QGIS parameter `asScriptCode` / `fromScriptCode` string definition.

The _default_value_ is applicable to number, string, boolean, range, color folder and file inputs.

The _from_ variable_ applies to Field and must point to _variable_name_ of vector input.

So the inputs can look like this:

`##Layer=vector` specifies that there will be variable `Layer` that will be a vector.

`##X=Field Layer` specifies that variable `X` will be field name taken from `Layer`.

`##Raster_Layer=raster` specifies that there will be variable `Layer` that will be a raster.

`##X=Band Raster_Layer` specifies that variable `X` will be raster band index taken from `Raster_Layer`.

`##Size=number 10` specifies that there will be variable `Size` that will be numeric, and a default value for `Size` will be `10`.

`##Extent=extent` specifies that there will be variable `Extent` that will be numeric of length `4` (_xmin_, _xmax_, _ymin_ and _ymax_ values).

`##CRS=crs` specifies that there will be variable `CRS` that will be `EPSG:____` string.

`##Range=range 0,1` specifies that the `Range` variable will be a two numeric values vector with names (min/max values). The parameter accepts default values, e.g. `0,1`. A range widget will be displayed for setting the values.

`##Color=color withopacity #FF0000CC` specifies that the `Color` variable will be a text string of the chosen color in hexadecimal format. This parameter will display a color selection widget. The parameter accepts default values, for example `#FF0000`. The opacity value depends on the `withopacity` option.

`##Date_Time=datetime` specifies that the `Date_Time` variable will be a `POSIXct` vector of length `1` of the date and time choosing from the `datetime` widget . The parameter does not accept default values, instead, the current date and time will set by default.

##### Enum

The basic enum syntax is `##var_enum=enum a;b;c` to select from values `a`, `b` or `c`. The value of `var_enum` in this case will be integer indicated position of the selected item in a list. So for example, if `a` is selected the value of `var_enum` will be `0`.

The approach described above works well for a wide range of applications but for **R** it is often not ideal. That is a reason why a new type of enum is available in script syntax.

The syntax is `##var_enum_string=enum literal a;b;c`. The important part here is the keyword `literal` (or more precisely `enum literal`) which specifies that the value from the select box to `var_enum_string` should be passed as a string. So if `b` is selected, then the value of `var_enum_string` will be `"b"`.

Enum also accept multiples choices in both, literal or numeric setups, i.e. `##var_enum_string=enum literal multiple a;b;c` or `##var_enum_string=enum multiple a;b;c`. The variables in R will behave in the same way as non-multiple setup.

#### Advanced specification

The inputs to R script are specified as: `QgsProcessingParameter|name|description|other_parameters_separated_by_pipe`.
The _other_ parameter_ separated_ by_ pipe_ can contain the `QgsProcessingParameter` specific parameters.
This metadata line is based on the QGIS definitions used in description file used by GRASS7, SAGA and others providers.

So the inputs can look like this:

`##QgsProcessingParameterFeatureSource|INPUT|Vector layer` specifies that there will be variable `INPUT` that will be a vector.

`##QgsProcessingParameterField|FIELDS|Attributes|None|INPUT|-1|False|False` specifies that there will be variable `FIELDS` that will be a field index.

`##QgsProcessingParameterRasterLayer|INPUT|Grid` specifies that there will be variable `INPUT` that will be a raster.

`##QgsProcessingParameterNumber|SIZE|Aggregation Size|QgsProcessingParameterNumber.Integer|10` specifies that there will be variable `Size` that will be numeric, and a default value for `Size` will be `10`.

`##QgsProcessingParameterEnum|METHOD|Method|[0] Sum;[1] Min;[2] Max` specifies that there will be variable `METHOD` that will be a value provided under `[]`.

`##QgsProcessingParameterVectorDestination|OUTPUT|Result` specifies that there will be variable `OUTPUT` that will be the destination file.


##### Feature source

QgsProcessingParameterFeatureSource|name|description|geometry type|default value|optional
* _name_ is mandatory
* _description_ is mandatory
* _geometry type_ is optional and the default value is `-1` for any geometry, the available values are `0` for point, `1` for line, `2` for polygon, `5` for table
* _default value_ is optional and the default value is `None`
* _optional_ is optional and the default value is `False`

`##QgsProcessingParameterFeatureSource|INPUT|Points|0` specifies that there will be variable `INPUT` that will be a vector point layer.

`##QgsProcessingParameterFeatureSource|INPUT|Lines|1` specifies that there will be variable `INPUT` that will be a vector line layer.

`##QgsProcessingParameterFeatureSource|INPUT|Polygons|2` specifies that there will be variable `INPUT` that will be a vector polygon layer.

`##QgsProcessingParameterFeatureSource|INPUT|Table|5` specifies that there will be variable `INPUT` that will be a vector layer to provide table.

`##QgsProcessingParameterFeatureSource|INPUT|Optional layer|-1|None|True` specifies that there will be variable `INPUT` that will be an optional vector layer.

##### Raster layer

QgsProcessingParameterRasterLayer|name|description|default value|optional
* _name_ is mandatory
* _description_ is mandatory
* _default value_ is optional and the default value is `None`
* _optional_ is optional and the default value is `False`

##### File or folder parameter

QgsProcessingParameterFile|name|description|behavior|extension|default value|optional|file filter
* _name_ is mandatory
* _description_ is mandatory
* _behavior_ is optional and the default value is `0` for file, `1` is for folder input parameter
* _extension_ is optional and specifies a file extension associated with the parameter (e.g. `html`). Use _file filter_ for a more flexible approach which allows for multiple file extensions. if _file filter_ is specified it takes precedence and _extension_ is emptied.
* _default value_ is optional and the default value is `None`
* _optional_ is optional and the default value is `False`
* _file filter_ is optional and specifies the available file extensions associted sith the parameter (e.g. `PNG Files (*.png);; JPG Files (*.jpg *.jpeg)`)

`##QgsProcessingParameterFile|in_file|Input file` specifies that there will be variable `in_file` that will be any file.

`##QgsProcessingParameterFile|in_folder|Input folder|1` specifies that there will be variable `in_folder` that will be a folder.

`##QgsProcessingParameterFile|in_gpkg|Input gpkg|0|gpkg` specifies that there will be variable `in_gpkg` that will be gpkg file.

`##QgsProcessingParameterFile|in_img|Input img|0|png|None|False|PNG Files (*.png);; JPG Files (*.jpg *.jpeg)`  specifies that there will be variable `in_img` that will be an image PNG or JPG.

#### QGIS Expression

A QGIS expression can be used as input for the script. The syntax is `r_variable_name=expression` followed by space and any valid QGIS expression. The expression is evaluated in QGIS before passing the result value script to R. This type of input is hidden from user of the script and can only be modified by editing the R script itself.

The following code:

`##qgis_expression=expression @qgis_version`

creates variable `qgis_expression` that will hold information about QGIS version on which the script was run (i.e. __3.22.0-Białowieża__).

`##example_geometry=expression make_circle( make_point(0, 0), 10)` creates R variable with name `example_geometry` that holds polygon created by the expression.

The variable type for R is determined from type of expression output in QGIS. So far these types are supported - string, integer, float, date, time, datetime, geometry and lists (arrays) of these types.

### Outputs

The outputs of R script are specified as `##variable_name=output output_type`. This line also specifies how tool UI will look in QGIS, as outputs are one section of the tool UI. In this specification _variable_name_ specifies variable from the script that will be exported back to QGIS, _output_type_ is one of the allowed types that can be returned from R script (layer, raster, folder, file, HTML, number, string, table).

So the outputs can look like this:

`##New_string=output string` specifies that a variable `New_string` will be set in the script.

`##New_number=output number` specifies that a variable `New_number` will be set in the script.

#### Layer outputs

For layer outputs, the line definition can end with the `noprompt` keyword. In this case, the `variable_name` has to be defined in the script. Otherwise, the UI will display a widget to let the user defined the output destination.

`##New_layer=output vector` specifies that the variable `New_layer` will be imported to QGIS as a vector layer.

`##New_raster=output raster` specifies that variable `New_raster` will be imported to QGIS as a raster layer.

`##New_table=output table` specifies that the variable `New_table` will be imported to QGIS as a vector layer without geometry (CSV file).

#### Folder and files outputs

Like layer outputs, the folder and files outputs the line definition can end with the `noprompt` keyword.

`##New_file=output file` specifies that there will be variable `New_file` that will be a file path with `.file` extension

`##New_csv=output file csv` specifies that there will be variable `New_csv` that will be a file path with `.csv` extension

`##New_folder=output folder` specifies that there will be variable `New_folder` that will be a folder path

### Printing from R to tool log

If any output of any line in R script should be outputted to tool log, it needs to be preceded by `>`. So, for example, the following code will print the number of rows in `Layer`.

```
>nrow(Layer)
```
