# Example with vector output

This scripts takes input vector data and randomly samples _Size_ points over it. The result is returned as a vector layer.

## Script

```
##Point pattern analysis=group
##Sample random points=name
##Layer=vector
##Size=number 10
##Output= output vector
Layer_sp = as_Spatial(Layer)
pts = spsample(Layer_sp,Size,type="random")
Output = SpatialPointsDataFrame(pts, as.data.frame(pts))
```

## Script lines description

1. **Point pattern analysis** is the group of the algorithm.
2. **Sample random points** is the name of the algorithm.
3. **Layer** is the input vector layer.
4. **Size** is the numerical parameter with a default value of 10.
5. **Output** is the vector layer that will be created by the algorithm.
6. Convert from sf format to older sp format, for which `spsample()` works
7. Call the spsample function of the sp library and pass it to all the input defined above.
8. Create the output vector with the SpatialPointsDataFrame function.

That’s it! Just run the algorithm with a vector layer you have in the QGIS Legend, choose a number of the random point, and you will get them in the QGIS Map Canvas.