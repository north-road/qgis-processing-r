##my test=name
##my group=group

##QgsProcessingParameterRasterLayer|in_raster|Input raster
##QgsProcessingParameterFeatureSource|in_vector|Input vector
##QgsProcessingParameterField|in_field|Input field|None|in_vector
##QgsProcessingParameterExtent|in_extent|Input extent
##QgsProcessingParameterCrs|in_crs|Input CRS
##QgsProcessingParameterString|in_string|Input String
##QgsProcessingParameterNumber|in_number|Input number
##QgsProcessingParameterEnum|in_enum|Input enum
##QgsProcessingParameterBoolean|in_bool|Input boolean

##QgsProcessingParameterFile|in_file|Input file
##QgsProcessingParameterFile|in_folder|Input folder|1
##QgsProcessingParameterFile|in_gpkg|Input gpkg|0|gpkg
##QgsProcessingParameterFile|in_img|Input img|0|png|None|False|PNG Files (*.png);; JPG Files (*.jpg *.jpeg)

##QgsProcessingParameterVectorDestination|param_vector_dest|Vector destination
##QgsProcessingParameterVectorDestination|param_vector_point_dest|Vector destination point|0
##QgsProcessingParameterVectorDestination|param_vector_line_dest|Vector destination line|1
##QgsProcessingParameterVectorDestination|param_vector_polygon_dest|Vector destination polygon|2
##QgsProcessingParameterVectorDestination|param_table_dest|Vector destination table|5
##QgsProcessingParameterRasterDestination|param_raster_dest|Raster destination

##QgsProcessingParameterFolderDestination|param_folder_dest|Folder destination
##QgsProcessingParameterFileDestination|param_file_dest|File destination
##QgsProcessingParameterFileDestination|param_html_dest|HTML File destination|HTML Files (*.html)
##QgsProcessingParameterFileDestination|param_csv_dest|CSV File destination|CSV Files (*.csv)
##QgsProcessingParameterFileDestination|param_img_dest|Img File destination|PNG Files (*.png);; JPG Files (*.jpg *.jpeg)

##out_vector=output vector noprompt
##out_table=output table noprompt
##out_raster=output raster noprompt
##out_number=output number
##out_string=output string
##out_layer=output layer
##out_folder=output folder noprompt
##out_html=output html noprompt
##out_file=output file noprompt
##out_csv=output file csv noprompt

library(sp)
i <- 1

