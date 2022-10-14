# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 13:37:59 2022

@author: wilkijam
"""

import pandas as pd
import streamlit as st


@st.cache
def load_data():
    df = pd.read_csv('https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv')
    return df

sourcedf = load_data()

#%% sidebar inputs

selYr = st.sidebar.selectbox('Select the year for analysis:', 
                             sorted(set(sourcedf['year']), reverse=True))
selMinPop = st.sidebar.number_input('Select the minimum population of country (in millions):', 
                                    min_value=0, value=1, step=1)
selRemX = st.sidebar.number_input('Select the number of countries to remove from top of highest per capita emitters',
                                  min_value=1, value=10, step=1)

@st.cache
def get_yr(df, year):
    df = df[df['year'] == year]
    df = df[df['iso_code'] != '']
    df = df[['country', 'year', 'iso_code', 'co2', 'co2_per_capita']]
    return df

df19 = get_yr(sourcedf, '2019')