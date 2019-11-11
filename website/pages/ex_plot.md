# Example of graphs output

This scripts takes input vector data and randomly samples _Size_ points over it. The result is returned as a vector layer.
s
## Script

```
##Basic statistics=group
##Graphs=name
##output_plots_to_html
##Layer=vector
##Field=Field Layer
qqnorm(Layer[[Field]])
qqline(Layer[[Field]])
```

## Script lines description

1. **Basic statistics** is the group of the algorithm.
2. **Graphs** is the name of the algorithm.
3. The script output plot or plots.
4. **Layer** is the input vector layer.
5. **Field** is the name of the field from _Layer_ whose values will be plotted.
6. Produce a standard QQ plot of the values from _Field_ of _Layer_.
7. Add a line to a “theoretical”, by default normal, quantile-quantile plot which passes through the probs quantiles, by default the first and third quartiles.

The plot is automatically added to the Result Viewer of Processing, and it can be open the location shown in the image.

![](./images/graph_location.jpg)