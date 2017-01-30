import bokeh.io
import pandas as pd

from bokeh.layouts import widgetbox, layout
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import Paragraph, Select, CheckboxGroup
from bokeh.palettes import Category10
from bokeh.plotting import Figure

# Number of dataframes/populations
num_df = 0


def plot_pop(pops=[], files=[]):
    """
    Function to plot populations in browser using Bokeh

    Args:
        pops (list): List of population objects to plot
        files (list): List of population files to plot (currently only works
                      with csv files - file an issue if you would like more
                      options)
    """

    lp = len(pops)
    lf = len(files)

    # Configure colours
    ld = lp + lf
    if ld < 3:
        colours = Category10[3][0:ld]
        colours = ['#1f77b4', '#ff7f0e']
    else:
        colours = Category10[ld]

    # Dataframes
    dfs = []

    def read(path):
        '''
        Mini-function to read in data

        Args:
            path (str): Path to file to read
        '''
        global num_df
        df = pd.read_csv(path)
        df['plot_colour'] = colours[num_df]
        df['plot_size'] = str((num_df+1)*5)
        dfs.append(df)
        num_df += 1

    # Check whether populations have been given as input
    if lp == 0 and lf == 0:
        print('Nothing to plot: plot arguments are empty')
        return

    # Get dataframe from populations
    elif lp > 0:
        for p in pops:
            read(p.values())

    # Get dataframe from files
    elif lf > 0:
        for f in files:
            read(f)

    # Check which overlapping attributes the populations have
    attrs = set(list(dfs[0]))
    if lp + lf > 1:
        for df in dfs[1:]:
            attrs.intersection_update(list(df))
    attrs = sorted(list(attrs))

    # Drop unhelpful attributes
    if 'detected' in attrs:
        attrs.remove('detected')

    # Create a new plot
    plot = Figure(title=None)

    # Add databases together
    df = pd.concat([d for d in dfs])

    # Convert data format
    source = ColumnDataSource(df)

    # Plot the data
    plot.scatter(x='gx',
                 y='gy',
                 color='plot_colour',
                 size='plot_size',
                 source=source)

    # Javascript to make the plot interactive
    code = """
           var data = source.get('data');
           var r = data[cb_obj.get('value')];
           var {var} = data[cb_obj.get('value')];
           //window.alert( "{var} " + cb_obj.get('value') + {var}  );
           for (i = 0; i < r.length; i++) {{
               {var}[i] = r[i] ;
               data['{var}'][i] = r[i];
           }}
           source.trigger('change');
           """

    # Interactive goodness
    callbackx = CustomJS(args=dict(source=source),
                         code=code.format(var='gx'))
    callbacky = CustomJS(args=dict(source=source),
                         code=code.format(var='gy'))
    callbackpop = CustomJS(args=dict(source=source),
                         code=code.format(var='gy'))

    # Add check boxes for toggling populations
    pop_ops = ['pop_1', 'pop_2']
    choose_pop = CheckboxGroup(name='Populations',
                               labels=pop_ops,
                               active=[i for i in range(ld)],
                               callback=callbackpop)

    # Add list boxes for selecting which columns to plot on the x and y axis
    xaxis_select = Select(title='X-axis:',
                          value='gx',
                          options=attrs,
                          callback=callbackx)
    yaxis_select = Select(title='Y-axis:',
                          value='gy',
                          options=attrs,
                          callback=callbacky)

    # Setup layout plot window
    title = Paragraph(text='frbpoppy')
    text = Paragraph(text='Please select options')
    inputs = widgetbox(title, text, choose_pop, xaxis_select, yaxis_select)
    panel = layout([[inputs, plot]])

    # Show the plot!
    bokeh.io.show(panel)