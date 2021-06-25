#Importando a bibliotecas
import dash
from dash.development.base_component import Component
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import pycountry

# -- FUNÇÕES --
def get_country_code(col):
    CODE = []
    for country in col:
        try:
            code = pycountry.countries.get(name=country).alpha_3
            CODE.append(code)
        except:
            CODE.append('None')
    return CODE

#Criando o aplicativo dash
app = dash.Dash(__name__)
server = app.server

#Carregando os dados
dataset = pd.read_csv('./Data/master.csv')

#Mudando o nome das colunas para facilitar
dataset = dataset.rename(columns={'HDI for year':'HDI',
                            'gdp_for_year ($)':'gdp_for_year',
                            'gdp_per_capita ($)':'gdp_per_capita'})

#Mudando a coluna gdp_for_year para int
dataset['gdp_for_year'] = dataset['gdp_for_year'].str.replace(",","")
dataset['gdp_for_year'] = dataset['gdp_for_year'].astype('int64')

#Considerando apenas os anos depois de 2016
dataset = dataset[dataset['year'] < 2016]

#groupbys
#Soma total de suícido por ano
suicide_per_year = dataset.groupby(dataset['year'])['suicides_no'].sum().reset_index()

#Suicidios totais por faixa etária
age_range_total = dataset.groupby(['age'])['suicides_no'].sum().reset_index()

#Suicidios totais por país
country_suicide = dataset.groupby(['country'])['suicides_no'].sum().reset_index().sort_values(by='suicides_no', ascending=False)
#Colocando o código dos paises
country_suicide['code'] = get_country_code(country_suicide.country)


#plots
#Suicidios por ano
suicide_per_year_plot = px.line(suicide_per_year, x='year', y='suicides_no', title="Número de suícidios por ano")
suicide_per_year_plot.update_traces(mode='lines+markers')
suicide_per_year_plot.update_layout(title_x=0.5)

#Suicidios por faixa etária
age_range_total_plot = px.pie(age_range_total, values='suicides_no', names='age', title='Faixa etária')
age_range_total_plot.update_layout(title_x=0.5)

#Suicidios por pais (mapa)
country_suicide_plot = px.choropleth(country_suicide, locations='code', color='suicides_no', color_continuous_scale='teal', hover_name='country')
country_suicide_plot.update_geos(projection_type='orthographic')
country_suicide_plot.update_layout(title='Países com maiores números de suícidios', title_x=0.5)

# (barrar)
country_suicide_bar = px.bar(country_suicide.head(10), x='country', y='suicides_no', color_continuous_scale='teal')
country_suicide_bar.update_layout(title='Países com maiores números de suicídios (em ordem)', title_x=0.5)

#Criando o layout
app.layout = html.Div([

    #Fazendo o título
    html.H1("Dashboard de taxa de suícidos entre 1987 e 2015", style={'text-align':'center'}),

    #Criando o gráfico
    dcc.Graph(id='line_graph', figure=suicide_per_year_plot, style={'width':'60%','display':'inline-block'}),
    dcc.Graph(id='pie_chart', figure=age_range_total_plot, style={'width':'30%', 'display':'inline-block'}),

    dcc.Graph(id='country', figure=country_suicide_plot, style={'width':'40%', 'display':'inline-block'}),
    dcc.Graph(id='country_bar', figure=country_suicide_bar, style={'width':'60%', 'display':'inline-block'})

])

if __name__ == '__main__':
    app.run_server()