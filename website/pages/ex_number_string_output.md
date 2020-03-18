# Example with number and string outputs

This script takes input vector data and one of its fields. The result is the minimum and maximum for a given field of the layer.

## Script

```
##Basic statistics=group
##Min_Max=name
##Layer=vector
##Field=Field Layer
##Min=output number
##Max=output number
##Summary=output string

Min <- min(Layer[[Field]])
Max <- max(Layer[[Field]])
Summary <- paste(Min, "to", Max, sep = " ")
```

## Script lines description

1. **Basic statistics** is the group of the algorithm.
2. **Min_Max** is the name of the algorithm.
3. **Layer** is the input vector layer.
4. **Field** is the name of a field from _Layer_.
5. **Min** is the name of the minimum output that will be created and returned to QGIS.
6. **Max** is the name of the maximum output that will be created and returned to QGIS.
7. **Summary** is the name of the string output that will be created and returned to QGIS.
8. Calculate minimum
9. Calculate maximum
10. Create the string

The outputs will be presented in QGIS as a dictionnary.