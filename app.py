import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
#from jupyter_dash import JupyterDash
#import dash_core_components as dcc
from dash import dcc # changed line above to this one
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = '''
**Pew Research is a generally reputable source for research on many topics, including the gender wage gap, which they have been studying for many years. [Here](https://www.pewresearch.org/fact-tank/2021/05/25/gender-pay-gap-facts/) is a summary of their findings for 2020. According to Pew Research, the wage gap is generally attributable to factors such as "educational attainment, occupational segregation and work experience", and the overall gap has remained relatively stable over the past ~15 years. In 2020, the median full-time female worker made about 84% of what their male counterparts made. It is noted that the gap for younger workers has been closing thanks to progress made in these factors, such as more women in managerial positions, though women still face issues related to workplace descrimination that help perpetuate the gap.**

**[This](https://blog.dol.gov/2021/03/19/5-facts-about-the-state-of-the-gender-pay-gap) blog on the *US Dept of Labor* quotes more granular statistics related to the role demographics like race play in the wage gap. What is interesting is the blog mentions the effect that the pandemic has had on women workers – the participation rate of women in the workforce was only 55.8%, "the same rate as April 1987".**

**The [General Social Survey](http://www.gss.norc.org/About-The-GSS) (GSS) is "the only full-probability, personal-interview survey designed to monitor changes in both social characteristics and attitudes currently being conducted in the United States." Its purpose is to collect data on American society through surveys; this has been ongoing for nearly 50 years. Questions cover general social issues, such as crime, education, and spending, while others are more specific to things like familial relations and how Americans view tradition family dynamics, such as women working vs. raising children. Data have been collected using methods to ensure the highest quality; "more than 130 papers have been published in the GSS Methodological Reports series."**
_______
'''

gss_tab = gss_clean.groupby('sex').agg({'income': 'mean', 
                                        'job_prestige': 'mean', 
                                        'socioeconomic_index': 'mean', 
                                        'education': 'mean'})

gss_tab = round(gss_tab.rename({'income': 'Avg. Income (USD)',
                'job_prestige': 'Avg. Job Prestige',
                'socioeconomic_index': 'Avg. Socio-Economic Idx',
                'education': 'Avg. Yrs Education'}, axis = 1), 2)

table = ff.create_table(gss_tab, index = True, index_title='Sex', height_constant = 15)

gss_clean.male_breadwinner = gss_clean.male_breadwinner.astype('category')
gss_clean['male_breadwinner'] = gss_clean['male_breadwinner'].cat.reorder_categories(['strongly agree',
                                                                             'agree',
                                                                             'disagree',
                                                                             'strongly disagree'])

gss_group = gss_clean.groupby(['sex', 'male_breadwinner']).agg({'id':'size'}).reset_index().rename({'sex':'Sex', 'id': 'Count'}, axis = 1)

bar = px.bar(gss_group, x='male_breadwinner', y='Count', color='Sex',
            labels={'male_breadwinner':'It is better for the husband to be sole breadwinner', 'Count':'Count Responses'},
            text='Count',
            barmode = 'group', color_discrete_map = {'male':'cornflowerblue', 'female':'coral'})
bar.update_layout(showlegend=True)
bar.update(layout=dict(title=dict(x=0.5)))

scatter = px.scatter(gss_clean, x='job_prestige', y='income', color = 'sex',
                 labels = {'job_prestige': 'Job Prestige', 'income': 'Income (in USD)'},
                 height=600, width=600,
                 trendline='ols',
                 hover_data={'education': True, 'socioeconomic_index': True},
                 range_x = [0, 100], color_discrete_map = {'male':'cornflowerblue', 'female':'coral'}
                )
# could adjust the hover_data dictionary to include the other columns with False if I 
# wanted to remove Sex, Income, and Job Prestige

box1 = px.box(gss_clean, x='income', y = 'sex', color = 'sex',
                   labels={'income':'Annual Income (USD)', 'sex':''},
             color_discrete_map = {'male':'cornflowerblue', 'female':'coral'})
box1.update_layout(showlegend=False)

box2 = px.box(gss_clean, x='job_prestige', y = 'sex', color = 'sex',
                   labels={'job_prestige':'Job Prestige Index', 'sex':''},
             color_discrete_map = {'male':'cornflowerblue', 'female':'coral'})
box2.update_layout(showlegend=False)

gss_sub = gss_clean[['income', 'sex', 'job_prestige']]
gss_sub['prest_bin'] = pd.cut(gss_sub['job_prestige'], bins = 6, labels = False)
gss_sub.dropna(inplace = True)

facet = px.box(gss_sub.sort_values('prest_bin'), x='income', y = 'sex', color = 'sex', 
             facet_col = 'prest_bin', facet_col_wrap = 2,
                   labels={'income':'Annual Income (USD)', 'prest_bin':  'Prestige Bin', 'sex':''},
             width=1000, height=600, color_discrete_map = {'male':'orange', 'female':'cornflowerblue'})
facet.update_layout(showlegend=False)


#app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
feats = ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork']
y_feats = ['sex', 'region', 'education']

app.layout = html.Div(
    children = [
        html.H1("General Social Survey (GSS) Exploration", style={
            'textAlign': 'left', 'color': 'blue', 'padding': '10px', 'backgroundColor': 'cornflowerblue'}),
        dcc.Markdown(children = markdown_text, style = {'backgroundColor': 'whitesmoke'}),
            
        html.Div([
            
            html.H4("Table 1: Average Features by Sex", style={
            'textAlign': 'center'}),
            
            dcc.Graph(figure=table)
            
        ], style = {'width':'70%', 'align': 'center', 'margin-left': 'auto','margin-right': 'auto', 'margin-bottom': '20px'}),

        html.Div([
            
            html.H4("Figure 1: Annual Income by Job Prestige Bin and Sex", style={
            'textAlign': 'center'}),
            
            dcc.Graph(figure=facet)
            
        ], style = {'width':'40%', 'float':'left'}),
        
        html.Div([
            
            html.H4("Figure 2: Annual Income and Job Prestige by Sex", style={
            'textAlign': 'center'}),
            
            dcc.Graph(figure=scatter)
            
        ], style = {'width':'54%', 'float':'right'}),
        
        
        html.Div([
            
            html.H4("Fig. 3a: Annual Income by Sex", style={
            'textAlign': 'center'}),
            
            dcc.Graph(figure=box1)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H4("Fig. 3b: Job Prestige by Sex", style={
            'textAlign': 'center'}),
            
            dcc.Graph(figure=box2)
            
        ], style = {'width':'48%', 'float':'right'}),
                
        
        
        html.Div(children = [
            html.H3("Figure 4: Interactive Bar Plot"),
            html.H3("X-axis feature"),
            
            dcc.Dropdown(id='x-axis',
                         options=[{'label': i, 'value': i} for i in feats],
                         value='male_breadwinner'),
            
            html.H3("Group"),
            
            dcc.Dropdown(id='color',
                         options=[{'label': i, 'value': i} for i in y_feats],
                        value = 'sex')
        
        ], style={'width': '25%', 'float': 'left'}),
        
        html.Div([
            
            dcc.Graph(id="graph")
        
        ], style={'width': '70%', 'float': 'right', 'background_color': 'wheat', "border":"2px wheat solid"}),


       
    
    ]
)
@app.callback(Output(component_id="graph",component_property="figure"), 
                  [Input(component_id='x-axis',component_property="value"),
                   Input(component_id='color',component_property="value")])

def make_figure(x, color):
    gss_group = gss_clean.groupby([color, x]).agg({'id':'size'}).reset_index().rename({'id': 'Count'}, axis = 1)
    return px.bar(gss_group, x=x, y='Count', color=color,
            text='Count', color_discrete_map = {'male':'cornflowerblue', 'female':'coral'},
            barmode = 'group')



if __name__ == '__main__':
    #app.run_server(mode='inline', debug=True, port=8022)
    app.run_server(debug=True)
