# Script syntax

The R scripts for the plugin use extension **.rsx**. These are classic R scripts with several metadata lines (starting with `##`) that define the interaction between QGIS and R. Metadata amongst other things specify how UI of the tool will look like.

The script loads necessary packages by itself. Combination of _sp_ and _rgdal_ or _sf_ for vector data and _sp_ and _rgdal_ or _raster_ for raster data. Any other packages need to be directly loaded using `library()` command in the script body.

## Metadata

`##script_name=name` _script_name_ is the name of the script; under this name, it will be listed in processing toolbox.

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

The inputs to R script are specified as: `variable_name=variable_type [default_value/from_variable]`. This metadata line also specifies how tool UI will look in QGIS, as inputs are one section of the tool UI. In this specification _variable_name_ is the name of the variable used in R script, _variable_type_ is a type of input variable from possible input types (vector, raster, table, number, string, boolean, Field).

The _default_value_ is applicable to number, string and boolean inputs.

The _from_ variable_ applies to Field and must point to _variable_name_ of vector input.

So the inputs can look like this:

`##Layer=vector` specifies that there will be variable `Layer` that will be a vector.

`##Size=number 10` specifies that there will be variable `Size` that will be numeric, and a default value for `Size` will be `10`.

`##X=Field Layer` specifies that variable `X` will be field name taken from `Layer`.

#### Enum

The basic enum syntax is `##var_enum=enum a;b;c` to select from values `a`, `b` or `c`. The value of `var_enum` in this case will be integer indicated position of the selected item in a list. So for example, if `a` is selected the value of `var_enum` will be `0`.

The approach described above works well for a wide range of applications but for **R** it is often not ideal. That is a reason why a new type of enum is available in script syntax.

The syntax is `##var_enum_string=enum literal a;b;c`. The important part here is the keyword `literal` (or more precisely `enum literal`) which specifies that the value from the select box to `var_enum_string` should be passed as a string. So if `b` is selected, then the value of `var_enum_string` will be `"a"`.

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