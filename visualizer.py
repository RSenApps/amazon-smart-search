import plotly.graph_objs as go
import numpy as np

def make_scatter(products_df, xcol, ycol, hovercol, tickprefix=''):
    f_scatter = go.FigureWidget([go.Scatter(x = products_df[xcol], 
                                           y = products_df[ycol], 
                                           mode = 'markers', 
                                           text = [x[:30] for x in products_df[hovercol]],
                                           selected_marker_size=5,
                                           marker_size = 3,
                                           selected_marker_color='red',
                                           opacity=.8)])
    scatter = f_scatter.data[0]

    N = len(products_df)
    scatter.x = scatter.x + np.random.rand(N)/100 *(products_df[xcol].max() - products_df[xcol].min())
    scatter.y = scatter.y + np.random.rand(N)/100 *(products_df[ycol].max() - products_df[ycol].min())
    scatter.selectedpoints = list(range(N))

    f_scatter.update_layout(
        xaxis_title=xcol,
        yaxis_title=ycol,
        xaxis_tickprefix = tickprefix,
        plot_bgcolor="#FFFFFF",
        xaxis_linecolor="#BCCCDC",
        yaxis_linecolor="#BCCCDC",
        xaxis_fixedrange=True,
        yaxis_fixedrange=True,
        dragmode="select",
        clickmode="select"
    )
    return f_scatter
