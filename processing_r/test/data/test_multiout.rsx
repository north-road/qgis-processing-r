##load_vector_using_rgdal
##Output=output vector
##OutputCSV=output table
##OutputFile=output file csv
##OutputNum=output number
##OutputStr=output string

OutputNum <- 4.5
OutputStr <- "value"

data <- read.table(header=TRUE, text='
 subject sex size
       1   M    7
       2   F    NA
       3   F    9
       4   M   11
 ')

write.csv2(data, outputFile, row.names = FALSE, na ="")