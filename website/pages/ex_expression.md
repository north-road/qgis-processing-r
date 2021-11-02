# Example with QGIS expression as inputs

This script takes several QGIS expression and prints their values from R.

## Script

```
##Expression examples=group
##Expressions=name
##qgis_version_info=expression @qgis_version_no
##example_value=expression 1+2+3
##example_geometry=expression make_circle( make_point(0, 0), 10)
##example_date=expression make_date(2020,5,4)
##example_time=expression make_time(13,45,30.5)
##example_array=expression array(2, 10, 'a')
>print(qgis_version_info)
>print(example_value)
>print(example_geometry)
>print(example_date)
>print(example_time)
>print(example_array)
```

## Script lines description

1. **Expression examples** is the group of the algorithm.
2. **Expressions** is the name of the algorithm.
3. **qgis_version_info** will be **string** after the expression is evaluated.
4. **example_value** will be number (**integer**) after the expression is evaluated.
5. **example_geometry** will be **sfg** (from **sf** package) after the expression is evaluated.
6. **example_date** will be **POSIXct** after the expression is evaluated.
7. **example_time** will be **Period** (from **lubridate** package) after the expression is evaluated.
8. **example_array** will be **list** of values after the expression is evaluated.

The rest of the lines prints the outputs in R. 

## Script output

The result may look like this (depending on QGIS version):

```
1] 32200
[1] 6
POLYGON ((3.06e-15 10, 1.736482 9.848078, 3.420201 9.396926, 5 8.660254, 6.427876 7.660444, 7.660444 6.427876, 8.660254 5, 9.396926 3.420201, 9.848078 1.736482, 10 -2.45e-15, 9.848078 -1.736482, 9.396926 -3.420201, 8.660254 -5, 7.660444 -6.427876, 6.427876 -7.660444, 5 -8.660254, 3.420201 -9.396926, 1.736482 -9.848078, -1.84e-15 -10, -1.736482 -9.848078, -3.420201 -9.396926, -5 -8.660254, -6.427876 -7.660444, -7.660444 -6.427876, -8.660254 -5, -9.396926 -3.420201, -9.848078 -1.736482, -10 1.22e-15, -9.848078 1.736482, -9.396926 3.420201, -8.660254 5, -7.660444 6.427876, -6.427876 7.660444, -5 8.660254, -3.420201 9.396926, -1.736482 9.848078, 3.06e-15 10))
[1] "2020-05-04 CEST"
[1] "13H 45M 30S"
[[1]]
[1] 2

[[2]]
[1] 10

[[3]]
[1] "a"
```

## Generated R script

The code that was actually generated from these expressions and passed to R looks like this:

```
qgis_version_info <- 32200
example_value <- 6
example_geometry <- sf::st_as_sfc("Polygon ((0.00000000000000306 10, 1.73648177666930459 9.84807753012207954, 3.42020143325668657 9.39692620785908517, 5.00000000000000533 8.66025403784438375, 6.42787609686539696 7.66044443118977814, 7.6604444311897808 6.42787609686539163, 8.66025403784438552 5, 9.39692620785908517 3.42020143325668124, 9.84807753012208131 1.73648177666929904, 10 -0.00000000000000245, 9.84807753012207954 -1.73648177666930392, 9.39692620785908517 -3.42020143325668569, 8.66025403784438907 -4.99999999999999734, 7.66044443118977902 -6.42787609686539607, 6.42787609686539163 -7.66044443118977991, 4.99999999999999645 -8.66025403784438907, 3.42020143325668613 -9.39692620785908517, 1.73648177666930414 -9.84807753012207954, -0.00000000000000184 -10, -1.73648177666930348 -9.84807753012207954, -3.42020143325668924 -9.39692620785908339, -5 -8.6602540378443873, -6.42787609686539607 -7.66044443118977902, -7.66044443118977991 -6.42787609686539252, -8.66025403784438552 -5.00000000000000089, -9.39692620785908161 -3.42020143325669057, -9.84807753012208131 -1.73648177666930015, -10 0.00000000000000122, -9.84807753012208131 1.73648177666930281, -9.39692620785908517 3.42020143325668435, -8.66025403784438552 5.00000000000000444, -7.66044443118977902 6.42787609686539607, -6.42787609686539252 7.66044443118977991, -5.00000000000000089 8.66025403784438552, -3.42020143325669101 9.39692620785908161, -1.73648177666930059 9.84807753012208131, 0.00000000000000306 10))")[[1]]
example_date <- as.POSIXct("2020-05-04", format = "%Y-%m-%d")
example_time <- lubridate::hms("13:45:30")
example_array <- list(2, 10, "a")
```
