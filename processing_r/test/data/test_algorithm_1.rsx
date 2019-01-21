##showplots
##dontuserasterpackage
##passfilenames

##polyg=vector
##polyg_category_id=field polyg
##table_category_id=field sizes_table
##sampling_size=field sizes_table
##output=output vector
library(sp)
i <- 1
category <- unique(polyg[[polyg_category_id]])[i]
categorymap <- polyg[polyg[[polyg_category_id]] == category,]
n <- sizes_table[which(sizes_table[[table_category_id]] == category), sampling_size]
spdf1 <- SpatialPointsDataFrame(spsample(categorymap, n, "random"), data = data.frame(category = rep(category, n)))

for (i in 2:length(unique(polyg[[polyg_category_id]]))){
  category <- unique(polyg[[polyg_category_id]])[i]
  categorymap <- polyg[polyg[[polyg_category_id]] == category,]
  n <- sizes_table[which(sizes_table[[table_category_id]] == category), sampling_size]
  spdf1 <- rbind(spdf1, SpatialPointsDataFrame(spsample(categorymap, n, "random"),
                                               data = data.frame(category = rep(category, n)))
  )
}
output = spdf1
