
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[70]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
import re


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[123]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[81]:

def get_list_of_university_towns():
    file = open('university_towns.txt').readlines()
    states = [line.split('[edit]')[0] for line in file if '[edit]' in line]
    file = [i.split(' (')[0] for i in file]

    file = '\n'.join(file) + '\n'

    file = re.split(('\[edit\]\n|'.join(states) + '\[edit\]\n'), file)[1:]
    schools = [{"State":states[state], "RegionName":school} for state in range(len(states)) for school in file[state].split('\n')  if school != '\n' and school != '']

    df = pd.DataFrame(schools)
    
    return df.iloc[:,::-1]

get_list_of_university_towns()


# In[117]:

def get_economy_df():
    economy_df = pd.read_excel('gdplev.xls', skiprows=5).iloc[2:,[4,6]]
    economy_df = economy_df.rename(index = str, columns = {'Unnamed: 4':'Quarter', 'GDP in billions of chained 2009 dollars.1':'GDP (billions)'})
    economy_df = economy_df[economy_df.Quarter >= '2000q1']
    
    return economy_df

def get_recession_start():
    economy_df = get_economy_df()
    
    economy_df['Next QT GDP'] = list(economy_df['GDP (billions)'].iloc[1:]) + [np.NAN]
    economy_df['Next 2 QT GDP'] = list(economy_df['GDP (billions)'].iloc[2:]) + 2*[np.NAN]
    
    economy_df['Recession Begin'] = (economy_df['GDP (billions)'] > 
                                     economy_df['Next QT GDP']) & (
                                    economy_df['Next QT GDP'] > 
                                    economy_df['Next 2 QT GDP'])

    start = economy_df[economy_df['Recession Begin'] == True]
    return start['Quarter'].values[1]
get_recession_start()


# In[116]:

def get_recession_end():
    economy_df = get_economy_df()
    
    economy_df['Prev QT GDP'] = [np.NAN] + list(economy_df['GDP (billions)'].iloc[:-1])
    economy_df['Prev 2 QT GDP'] = 2*[np.NAN] + list(economy_df['GDP (billions)'].iloc[:-2])
    
    economy_df['Recession End'] = (economy_df['GDP (billions)'] >
                                   economy_df['Prev QT GDP']) & (
                                economy_df['Prev QT GDP'] > 
                                economy_df['Prev 2 QT GDP']) & (economy_df['Quarter'] > get_recession_start())
    
    end = economy_df[economy_df['Recession End'] == True]
    return end['Quarter'].values[0]
get_recession_end()


# In[119]:

def get_recession_bottom():
    economy_df = get_economy_df()
    economy_df = economy_df[(economy_df.Quarter >= get_recession_start()) & (economy_df.Quarter <= get_recession_end())]
    bottom = economy_df[economy_df['GDP (billions)'] == economy_df['GDP (billions)'].min()]

    return bottom['Quarter'].values[0]

get_recession_bottom()


# In[125]:

def convert_housing_data_to_quarters():
    housing_df = pd.read_csv('City_Zhvi_AllHomes.csv')
    
    for year in range(2000,2017):
        for quarter in range(1,5):
            
            if quarter == 4 and year == 2016:
                break
            
            new_column_name = '{0}q{1}'.format(year, quarter)
            begin_month = (quarter-1)*3 + 1
            end_month = quarter*3
            begin_column = '{0}-{1:02d}'.format(year,begin_month)
            end_column = '{0}-{1:02d}'.format(year,end_month)
            
            if quarter == 3 and year == 2016:
                new_column_name = '2016q3'
                begin_month = 6
                end_month = 8
                begin_column = '{0}-{1:02d}'.format(year,begin_month)
                end_column = '{0}-{1:02d}'.format(year,end_month)                
            
            data = housing_df.loc[:,begin_column:end_column]
            
            housing_df[new_column_name] = data.mean(axis = 1)
    housing_df['State'] = housing_df['State'].apply(lambda x: states[x])  
    housing_df = housing_df.set_index(['State','RegionName']) 
    
    begin = housing_df.columns.get_loc('1996-04')
    end = housing_df.columns.get_loc('2016-08')
    
    housing_df.drop(housing_df.columns[begin:end+1], axis=1, inplace = True)
    housing_df.drop(housing_df.columns[0:4], axis=1, inplace = True)
    
    return housing_df

convert_housing_data_to_quarters()


# In[ ]:

def run_ttest():
    recession_start = get_recession_start()
    recession_end = get_recession_end()
    recession_bottom = get_recession_bottom()
    
    university_towns = get_list_of_university_towns()
    university_towns = university_towns.set_index(['State', 'RegionName'])
    
    housing_df = convert_housing_data_to_quarters()
    
    prices_start = housing_df[recession_start]
    prices_end = housing_df[recession_end]
    
    housing_df['Ratio'] = prices_start/prices_end
    
    ratio_uni = housing_df.loc[list(university_towns.index)]['Ratio'].dropna()
    ratio_not_uni_indices = set(housing_df.index) - set(ratio_uni.index)
    ratio_not_uni = housing_df.loc[list(ratio_not_uni_indices),:]['Ratio'].dropna()
    
    statistic, p_value = tuple(ttest_ind(ratio_uni, ratio_not_uni))
    outcome = statistic < 0
    different = p_value < 0.05
    better = ["non-university town", "university town"]

    return (different, p_value, better[outcome])

run_ttest()

