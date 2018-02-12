import colorlover as cl
import calendar
import pandas as pd
import numpy as np


###########
# Private #
###########

def _get_month_abbriviations():
    """ Returns a list of month names

    :return:
    months  : array
    """
    months = []
    for i in range(1, 13, 3):
        months.append(calendar.month_name[i])
    return months


###########
# Public #
###########

def get_hex_colors(colors="Greys"):
    """ Creates an array of hex coded colors.

    :param colors: string color group, Available colors can be found on # https://plot.ly/ipython-notebooks/color-scales/.
    :return: array
    """
    hex_colors = []
    num_colors = cl.to_numeric(cl.scales['9']['seq'][colors])
    for num_color in num_colors:
        num_color = [int(x) for x in num_color]
        num_color = '#%02x%02x%02x' % tuple(num_color)
        hex_colors.append(num_color)
    return hex_colors


def get_price_value_pct(price_value):
    """ Column name for price percentage

    :return:
    colname     : string
    """
    col_name = price_value + '_pct'
    return col_name


def add_day_week_year_to_df(df):
    """ Give dataframe a datetimeindex and add day, week and year as additional coluims to dataframe

    :param df: dataframe, 'Date' column required.

    :return:
    df      : dataframe
    """
    df = df.set_index(pd.DatetimeIndex(df['Date']))
    df['day'] = df['Date'].dt.dayofyear
    df['week'] = [int(x / 7) for x in df['day']]
    df['year'] = df['Date'].dt.year
    return df


def calculate_pct_change(df, crypto, rate):
    """ Calculate the crypto's percentage change with years start

    :param df: dataframe

    :return:
    df      : dataframe
    """
    colpct = get_price_value_pct(crypto)
    df[colpct] = df.groupby(['year'])[rate].transform(lambda x: (x / x[len(x) - 1]))
    return df


def format_as_x(arr):
    """ Format floats as multiplication factor

    :param arr: float array
    :return:    string array
    """
    return ['{:.1f}x'.format(x) for x in arr]


def format_yearly_graph_data(data_year, line_color, line_width, rate, colpct):
    """ Transform the yearly data to plotly ready format

    :param data_year:   dataframe
    :param line_color:  string
    :param line_width:  float
    :param rate:        string
    :param colpct:      string
    :return:
    data dict plotly
    annotation dict plotly
    """

    dates_year = data_year.groupby("week", as_index=False).min()

    tick_text = []
    for multiple, price in zip(format_as_x(dates_year[colpct]), dates_year[rate]):
        tick_text.append('{} - ${}'.format(multiple, price))

    data = dict(
        type='scatter',
        mode='lines',
        name=dates_year['year'][0],
        x=dates_year['week'],
        y=dates_year[colpct],
        text=tick_text,
        hoverinfo='text',
        line=dict(
            shape="spline",
            smoothing="2",
            color=line_color,
            width=line_width
        )
    )

    annotation = dict(
        x=max(dates_year['week']) + 1,
        y=np.log10(dates_year[colpct][len(dates_year) - 1]),
        text=dates_year["year"][0],
        font=dict(
            family='Arial',
            size=16,
            color=line_color
        ),
        showarrow=False)
    return data, annotation


def format_graph_layout(crypto, minpct, maxpct):
    """ Format graph layout

    :param crypto: string
    :param minpct: float
    :param maxpct: float
    :return:
    layout dict plotly
    """
    x_tick_vals, x_tick_text = get_x_ticks()
    y_tick_vals, y_tick_text = get_y_ticks(minpct, maxpct)

    layout = dict(
        title='{}\'s yearly price changes '.format(crypto.title()),
        autosize=True,
        height=600,
        xaxis=dict(
            title='Month',
            tickvals=x_tick_vals,
            ticktext=x_tick_text
        ),
        yaxis=dict(
            title='Change since 1 jan that year',
            type='log',
            tickvals=y_tick_vals,
            ticktext=y_tick_text
        ),
        showlegend=False

    )
    return layout


def get_x_ticks():
    """ X ticks currently have 4

    :return:
    x_tick_vals : array
    x_tick_text : array
    """
    x_tick_vals = np.arange(3, 55, 13)
    x_tick_text = _get_month_abbriviations()
    return x_tick_vals, x_tick_text


def get_y_ticks(y_min, y_max):
    """ Determine the number of y ticks. steps are 1,3,10 .. and get the smallest set which contain all the y values

    :param y_min: float
    :param y_max: float

    :return:
    y_tick_vals : array
    y_tick_text : array
    """
    exponents = list(range(-5, 5))
    ones = [float(10 ** x) for x in exponents]
    threes = [float((10 ** x) * 3) for x in exponents]
    ones.extend(threes)
    ones_threes = np.asarray(ones)
    y_min = ones_threes[ones_threes < y_min].max()
    y_max = ones_threes[ones_threes > y_max].min()
    y_tick_vals = ones_threes[np.logical_and(ones_threes >= y_min, ones_threes < y_max)]
    y_tick_text = format_as_x(y_tick_vals)
    return y_tick_vals, y_tick_text
