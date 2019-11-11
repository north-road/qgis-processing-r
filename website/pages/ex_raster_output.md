# Example with raster output

This scripts takes point layer and a field name as an input and performs automatic kriging. The returned value is a raster layer of interpolated values.

## Script

```
##Basic statistics=group
##Krige value=name
##load_vector_using_rgdal
##Layer=vector
##Field=Field Layer
##Output=output raster
library("automap")
table = as.data.frame(Layer)
coordinates(table)= ~coords.x1+coords.x2
c = Layer[[Field]]
kriging_result = autoKrige(c~1, table)
prediction = raster(kriging_result$krige_output)
Output = prediction
```