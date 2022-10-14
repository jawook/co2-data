# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 13:37:59 2022

@author: wilkijam
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

clrs = px.colors.qualitative.T10

#%% retrieve data from OWID
@st.cache
def loadData():
    df = pd.read_csv('https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv')
    return df

sourcedf = loadData()

#%% retrieve region data from github and merge to OWID data
@st.cache
def loadRegions():
    df = pd.read_csv('https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/raw/master/all/all.csv')
    return df

regdf = loadRegions()
sourcedf = pd.merge(left=sourcedf, right=regdf, left_on='iso_code', 
                    right_on='alpha-3', how='left')

#%% sidebar inputs
selYr = st.sidebar.selectbox('Select the year for analysis:', 
                             sorted(set(sourcedf['year']), reverse=True))
selMinPop = st.sidebar.number_input('Select the minimum population of country (in millions):', 
                                    min_value=0, value=1, step=1)
selRemX = st.sidebar.number_input('Select the number of countries to remove from top of highest per capita emitters',
                                  min_value=1, value=10, step=1)

def getdf(df, year, minpop):
    newdf = df[df['year'] == year]
    newdf = newdf[newdf['iso_code'] != '']
    newdf = newdf[['country', 'year', 'iso_code', 'population', 'co2', 
             'co2_per_capita', 'region', 'sub-region']]
    newdf = newdf[newdf['population'] >= minpop*1000000]
    newdf = newdf[newdf['co2'].notna() & newdf['co2_per_capita'].notna() & 
                  newdf['iso_code'].notna()]
    return newdf

yrDf = getdf(sourcedf, selYr, selMinPop)
numCountry = yrDf['country'].nunique()
cutoff = min(yrDf.nlargest(selRemX, 'co2_per_capita')['co2_per_capita'])
yrDf['topN'] = ['Top '+ 
                str(selRemX) if x >= cutoff else 'Bottom ' + 
                str(numCountry-selRemX) for x in yrDf['co2_per_capita']]

st.markdown('#### CO<sub>2</sub> Emissions per Capita by Country in ' + str(selYr),
            unsafe_allow_html=True)
st.markdown('###### _Top ' + str(selRemX) + 
            ' highlighted in orange; tonnes/year_')
chrBarPerCap = px.bar(yrDf, x='country', y='co2_per_capita', color='topN',
                      color_discrete_sequence=clrs)
chrBarPerCap.update_xaxes(categoryorder='total descending', title=None)
chrBarPerCap.update_yaxes(title='Total CO<sub>2</sub> Emissionse per Capita',
                          tickformat='.1f')
chrBarPerCap.update_layout(margin={'l': 0, 't': 0, 'r': 0, 'b':0}, 
                           paper_bgcolor='rgba(0,0,0,0)',
                           plot_bgcolor='rgba(0,0,0,0)',
                           showlegend=False)
chrBarPerCap.update_traces(hovertemplate='<b>%{x}</b><br>%{y}')
st.plotly_chart(chrBarPerCap, use_container_width=True)

st.markdown('#### Total CO<sub>2</sub> Emissions by Country' + str(selYr),
            unsafe_allow_html=True)
chrTreeTotal = px.treemap(yrDf, values='co2', 
                          path=[px.Constant('All Included Countries'),
                                'topN', 'country'],
                          color_discrete_sequence=clrs)
chrTreeTotal.update_layout(uniformtext=dict(minsize=14, mode='hide'),
                           margin={'l': 0, 't': 0, 'r': 0, 'b':0})
chrBarPerCap.update_traces(hovertemplate='<b>%{Label}</b><br>%{value}')
st.plotly_chart(chrTreeTotal, use_container_width=True)