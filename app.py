import dash
import dash_core_components as dcc
import dash_html_components as html

from datetime import datetime as dt
from dateutil import parser
from parsers import parser_cmc
from helpers import helpers


def get_main_figure(df, crypto, rate):
    """ Generates the main graph based on user inputs

    :param df:      pd.DataFrame
    :param crypto:  string
    :param rate:    string
    :return:
    dict
    """
    data = []
    annotations = []

    years = list(range(min(df['year']), max(df['year']) + 1))
    colpct = helpers.get_price_value_pct(crypto)
    colors = helpers.get_hex_colors()

    for i, year in enumerate(years):
        data_year = df[df['year'] == year]
        color_pos = 9 - (len(years) - i)
        line_color = colors[color_pos]
        line_width = 1.5
        if year == max(df['year']):
            line_color = 'blue'
            line_width = 4

        graph_data_year, graph_annotations_year = helpers.format_yearly_graph_data(data_year, line_color, line_width,
                                                                                   rate, colpct)

        data.append(graph_data_year)
        annotations.append(graph_annotations_year)

    # Red dashed line of 1x
    data.append(dict(
        type='scatter',
        mode='lines',
        name='1.0x',
        x=[1, 55],
        y=[1, 1],
        line=dict(
            color='red',
            width=1,
            dash='dot'
        )
    ))

    layout = helpers.format_graph_layout(crypto, min(df[colpct]), max(df[colpct]))
    layout['annotations'] = annotations

    return dict(data=data, layout=layout)


app = dash.Dash()
app.title = 'Yearly crypto price changes'

app.layout = html.Div([
    html.Div([
        html.H4("Crypto price changes over time - how does the price evolve in a given year?")
    ], className='col s12 indigo'),
    html.Div([
        html.H5('Select a crypto:'),
        dcc.Dropdown(
            id='dropdown-crypto',
            options=parser_cmc.get_markets(),
            value='bitcoin'
        ),
        html.H5('Choose period:'),
        html.Div([
            dcc.DatePickerSingle(
                id='datepicker-start',
                date=dt(2013, 1, 1)
            ),
            dcc.DatePickerSingle(
                id='datepicker-end',
                date=dt.today()
            )
        ]),
        html.H5('Select price rate:'),
        dcc.Dropdown(
            id='radio-rate',
            options=[
                {'label': 'Open', 'value': 'Open'},
                {'label': 'High', 'value': 'High'},
                {'label': 'Low', 'value': 'Low'},
                {'label': 'Close', 'value': 'Close'}
            ],
            value='Open'
        ),
        html.P(),
        html.A([html.Img(src='https://assets-cdn.github.com/images/modules/logos_page/GitHub-Mark.png', width='50px',
                         height='50px')],
               href='https://github.com/fathomson/CryptoPriceChanges', target='_blank'),
        html.A([html.Img(src='https://content.linkedin.com/content/dam/engineering/en-us/blog/migrated/linkedin.png',
                         width='50px', height='50px')],
               href='https://nl.linkedin.com/in/fathomson', target='_blank')
    ], className='col s3 grey lighten-4', style={'height': '100%'}),
    html.Div([
        dcc.Graph(id='graph-historical')
    ], className='col s9 19')
], className='row', style={'height': '100vh', 'margin-bottom': '-20px'})


@app.callback(
    dash.dependencies.Output('graph-historical', 'figure'),
    [dash.dependencies.Input('dropdown-crypto', 'value'),
     dash.dependencies.Input('datepicker-start', 'date'),
     dash.dependencies.Input('datepicker-end', 'date'),
     dash.dependencies.Input('radio-rate', 'value')])
def update_graph(crypto, start, end, rate):
    start = parser.parse(start).strftime("%Y%m%d")
    end = parser.parse(end).strftime("%Y%m%d")
    pcmc = parser_cmc.Historical(crypto=crypto, start=start, end=end, rate=rate)
    return get_main_figure(pcmc.get_cmc_historical_data(), crypto, rate)


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css",
                "https://codepen.io/chriddyp/pen/brPBPO.css"]
for css in external_css:
    app.css.append_css({"external_url": css})

external_scripts = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js"]
for script in external_scripts:
    app.scripts.append_script({"external_url": script})

if __name__ == '__main__':
    app.run_server(debug=True)  # , host='0.0.0.0'
