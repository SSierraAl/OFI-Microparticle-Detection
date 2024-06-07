import numpy as np
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, RangeTool
from bokeh.plotting import figure, curdoc

# Leer los datos del archivo .npy
data = np.load('./DataEXP/30ul 1 seg 5 steps fast/Calib_0.00797_5.npy')

# Crear índices para las fechas (usando números enteros consecutivos)
dates = np.arange(len(data))

source = ColumnDataSource(data=dict(x=dates, y=data))

p = figure(height=400, width=1400, tools="xpan", toolbar_location=None,
           x_axis_label='Index', x_axis_location="above",
           background_fill_color="#efefef", x_range=(dates[1500], dates[10000]))

p.line('x', 'y', source=source)
p.yaxis.axis_label = 'Value'

select = figure(title="Drag the middle and edges of the selection box to change the range above",
                height=130, width=1400, y_range=p.y_range,
                x_axis_label='Index', y_axis_type=None,
                tools="", toolbar_location=None, background_fill_color="#efefef")

range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

select.line('x', 'y', source=source)
select.ygrid.grid_line_color = None
select.add_tools(range_tool)
select.toolbar.active_multi = range_tool

# Crear una función de callback que se llamará cuando cambien los límites de la RangeTool
def range_tool_callback(attr, old, new):
    start = range_tool.x_range.start
    end = range_tool.x_range.end
    print("RangeTool start:", start)
    print("RangeTool end:", end)

# Agregar el callback a la RangeTool
range_tool.x_range.on_change('start', range_tool_callback)
range_tool.x_range.on_change('end', range_tool_callback)

# Crear el layout
layout = column(select, p)

# Añadir el layout a la aplicación Bokeh Server
curdoc().add_root(layout)