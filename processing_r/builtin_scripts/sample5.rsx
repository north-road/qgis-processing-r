##Example scripts=group
##Expressions=name
##my_r_variable=expression 1+2+3
##qgis_version=expression @qgis_version_no
##geometry=expression make_circle( make_point(0, 0), 10)
##test_date=expression make_date(2020,5,4)
##test_time=expression make_time(13,45,30.5)
##array=expression array(2, 10, 'a')
>print(my_r_variable)
>print(qgis_version)
>print(geometry)
>print(class(geometry))
>print(test_date)
>print(test_time)
>print(array)