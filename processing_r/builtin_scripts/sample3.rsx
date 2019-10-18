##test_sp=name
##load_vector_using_rgdal
##Layer=vector
##output= output vector

>print("--------------------------------------------------------")
>head(Layer)
>print("--------------------------------------------------------")
>proj4string(Layer)
>print("--------------------------------------------------------")
output <- Layer[1,]
