sfrom dash import Dash, dcc, html, callback, Output, Input, dash_table
import pandas as pd
import plotly.express as px

#connect to the data
df=pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')
#print(df[:11])
#body of website
markdown_text='''
## Is there a relationship between the contribution of the industry sector to GDP (value added %) and CO2 emissions per capita in an economy??

Are the two indicators correlated. i.e., does the occurence of one(x) influence the occurence of another(y)??


   >_Select the variable for X axis from the LHS input panels_


   >_Select the variable for Y axis from the RHS input panels_

#### Time Series
   > What do the time-series graphs tell us the trend is??

   
   > Update the time series graphs to the right when you hover over the points in the scatter plot
'''

#import css
styl=['https://codepen.io/chriddyp/pen/bWLwgP.css']
#initialise the app and incorporate css
app=Dash(__name__, external_stylesheets=styl)
server=app.server

#define the app layout
app.layout=html.Div([
    html.Div([
        html.H1('Does X affect Y?'),
        html.Hr(),
        dcc.Markdown(children=markdown_text)
    ]),
    html.Div([
        html.Div([
            dcc.Dropdown(
                df['Indicator Name'].unique(),
                'Industry, value added (% of GDP)',
                id='independent_var'
            ),
            dcc.RadioItems(
                ['Linear','Log'],
                'Log',
                inline=True,
                id='dt_type_x',
                labelStyle={'display':'inline-block','marginTop':'5px'})
        ],style={'display':'inline-block','width':'49%'}),
        html.Div([
            dcc.Dropdown(
                df['Indicator Name'].unique(),
                'CO2 emissions (metric tons per capita)',
                id='dependent_var'),
            dcc.RadioItems(
                ['Linear','Log'],
                'Log',
                inline=True,
                id='dt_type_y',
                labelStyle={'display':'inline-block','marginTop':'5px'})
        ],style={'display':'inline-block','width':'49%', 'float':'right'})
    ], style={'padding':'10px 5px'}),
    html.Div([
        dcc.Graph(id='graf', hoverData={'points':[{'customdata':'Kenya'}]})
    ], style={'display':'inline-block','width':'49%','padding':'0 20'}),
    html.Div([
        dcc.Graph(id='xt_graf'),
        dcc.Graph(id='yt_graf')
    ], style={'display':'inline-block','width':'49%', 'float':'right'}),
    html.Div([
        dcc.Slider(
            df['Year'].min(),
            df['Year'].max(),
            step=None,
            value=1977,
            id='sliida',
            marks={str(year):str(year) for year in df['Year'].unique()})
    ], style={'display':'inline-block','width':'49%','padding':'0px 20px 20px 20px'}),
    html.Div([
        html.H4('Data Used'),
        html.Hr(),
        dash_table.DataTable(data=df.to_dict('records'), page_size=11, style_table={'overflowX':'auto'})
    ])
])

'''callback decorators and time series creation function'''
#callback decorator + function to update scatter plot -'Graf'
@callback(
    Output('graf','figure'),
    Input('independent_var','value'),
    Input('dependent_var','value'),
    Input('dt_type_x','value'),
    Input('dt_type_y','value'),
    Input('sliida','value')
)
def updateGraf(indep_var, dep_var, type_x, type_y, time):
    dff=df[df['Year']==time]
    fig=px.scatter(
        x=dff[dff['Indicator Name']==indep_var]['Value'],
        y=dff[dff['Indicator Name']==dep_var]['Value'],
        hover_name=dff[dff['Indicator Name']==dep_var]['Country Name'])
    fig.update_traces(customdata=dff[dff['Indicator Name']==dep_var]['Country Name'])
    fig.update_layout(margin={'l':40,'b':40,'t':10,'r':0}, hovermode='closest')
    fig.update_xaxes(title=indep_var,
                    type='log' if type_x == 'Log' else 'linear')
    fig.update_yaxes(title=dep_var,
                    type='log' if type_y == 'Log' else 'linear')
    return fig

#function that creates the time series 
def create_time_series(dff, axis_type, title):
    fig=px.scatter(dff, x='Year', y='Value')
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(type='log' if axis_type=='Log' else 'linear')
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                      xref='paper', yref='paper', showarrow=False, align='left',
                      text=title)
    fig.update_layout(height=225, margin={'l':20,'b':30,'r':10,'t':10})
    return fig
#callback decorators+functions that update the time series graphs
#1 (decorator)- updates the x_Time_series graph
@callback(
    Output('xt_graf','figure'),
    Input('graf','hoverData'),
    Input('independent_var','value'),
    Input('dt_type_x','value'),
)
def updateXTseries(hoverData, indep_var, axis_type):
    country_name=hoverData['points'][0]['customdata']
    dff=df[df['Country Name']==country_name]
    dff=dff[dff['Indicator Name']==indep_var]
    title = '<b>{}</b><br>{}'.format(country_name, indep_var)
    return create_time_series(dff, axis_type, title)

#2 (decorator)- updates the y_Time_series graph
@callback(
    Output('yt_graf','figure'),
    Input('graf','hoverData'),
    Input('dependent_var','value'),
    Input('dt_type_y','value'),
)
def updateXTseries(hoverData, dep_var, axis_type):
    dff=df[df['Country Name']==hoverData['points'][0]['customdata']]
    dff=dff[dff['Indicator Name']==dep_var]
    return create_time_series(dff, axis_type, dep_var)

#run the app
if __name__ == '__main__':
    app.run(debug=True, port=2050)
