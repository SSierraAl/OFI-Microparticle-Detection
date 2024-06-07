from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.layouts import gridplot, layout
from bokeh.models import LinearColorMapper,LassoSelectTool, CustomJS, MultiChoice, HoverTool,PreText, NumeralTickFormatter,BoxSelectTool, TextInput,TabPanel, Tabs
from bokeh.layouts import column as column_layout
import os
from os.path import dirname, join

import numpy as np
from bokeh.layouts import gridplot
from bokeh.models import LinearAxis, Range1d, Select
from bokeh.plotting import figure, show,curdoc
from bokeh.models import Button, TextInput,DataTable, NumberFormatter, StringFormatter, StringEditor, NumberEditor,TableColumn
from bokeh.events import ButtonClick
from bokeh.palettes import Viridis256

import numpy as np
from scipy import signal
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, RangeTool, Div
from bokeh.plotting import figure, show
from scipy.signal import butter, filtfilt,spectrogram
import pandas as pd

from scipy.optimize import curve_fit

import random