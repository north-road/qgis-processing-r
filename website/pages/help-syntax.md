# Help syntax

The R scripts for the plugin contain lines of metadata and R commands that perform a procedure. However, it is also possible to add help documentation for the user of that script.

## Help files

The documentation of the script functionalities and its parameters requires an extra file containing the descriptive texts of each input or output parameter. The help file must be located in the same directory and have the name of the script with extension  **.rsx.help**.

The content of this file is a JSON object with the parameter descriptions. For example, suppose we have added a script `"simple_scatterplot.rsx"` with the following content:

```r
##Example scripts=group
##Scatterplot=name
##output_plots_to_html
##Layer=vector
##X=Field Layer
##Y=Field Layer

# simple scatterplot
plot(Layer[[X]], Layer[[Y]])
```
 
The help file should be named `"simple_scatterplot.rsx.help"` and its content should be a JSON object as follows:

```json
{
"Layer": "Vector Layer",
"X": "Field from Layer to be used as x-axis variable",
"Y": "Field from Layer to be used as y-axis variable"
}
```

This file can already be used in the script. Parameters that are not described in the help file will be omitted from the help section. Note that each parameter is composed of a pair of `key:value` strings and are separated from other parameters by a comma (,).  

There are special parameters that do not have a user-defined name. These are:

- `"RPLOTS"`, 
- `"R_CONSOLE_OUTPUT"`, 
- `"ALG_DESC"`,
- `"ALG_VERSION"`, 
- `"ALG_CREATOR"`,
- `"ALG_HELP_CREATOR"`

If added to the help file, it will allow for more descriptive information to be appended to the script. Continuing with the previous example we can add to the JSON the following information:

```json
{
"Layer": "Vector Layer",
"X": "Field from Layer to be used as x-axis variable",
"Y": "Field from Layer to be used as y-axis variable",
"RPLOTS": "Output path for html file with the scatterplot",
"ALG_DESC": "This file creates a simple scatterplot from two fields in a vector layer",
"ALG_CREATOR": "Name of algorithm creator",
"ALG_HELP_CREATOR": "Name of help creator",
"ALG_VERSION": "0.0.1"
}
```

## In-line help
 
As of version 3.2.0 of the plugin, it is also possible to enter the documentation as lines in the same script. lines in the script itself. This makes it possible to dispense with the **.rsx.help** file.  This requires entering lines starting with the characters `#'`. Let's see how the above example should be written.

```r
##Example scripts=group
##Scatterplot=name
##output_plots_to_html
##Layer=vector
##X=Field Layer
##Y=Field Layer

# simple scatterplot
plot(Layer[[X]], Layer[[Y]])

#' Layer: Vector Layer
#' X: Field from Layer to be used as x-axis variable
#' Y: Field from Layer to be used as y-axis variable
#' RPLOTS: Output path for html file with the scatterplot
#' ALG_DESC: This file creates a simple scatterplot from 
#'         : two fields in a vector layer
#' ALG_CREATOR: Name of algorithm creator
#' ALG_HELP_CREATOR: Name of help creator
#' ALG_VERSION: 0.0.1
```

Note that this form also allows you to enter the description of a parameter on multiple lines. For which you are required to enter a colon (`:`) after the `#'` characters.
