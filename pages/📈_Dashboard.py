import streamlit as st
import pandas as pd
import numpy as np

st.markdown("# Dashboard")
st.sidebar.markdown("# Dashboard")

# On the side bar -- data set markers
geo_resolution = st.sidebar.selectbox(
     'Geographical resolution',
     ('gadm0', 'gadm1'), index=0)

source = st.sidebar.selectbox(
     'Variable source',
     ("CRU TS", "ERA5", "UDelaware", "CSIC"), index=0)

variable = st.sidebar.selectbox(
     'Variable',
     ("temperature", "precipitation", "SPEI"), index=0)

# CSIC is the only that provides SPEI -- check consistency
if (source == 'CSIC' and variable != 'spei'):
    st.warning('Warning: CSIC provides only variable SPEI', icon="⚠️")

if (source != 'spei' and variable == 'CSIC'):
    st.warning('Warning: variable SPEI is only provided by CSIC', icon="⚠️")

weight = st.sidebar.selectbox(
     'Weighting type',
     ('population density 2015', 'night lights 2008', 'unweighted'), index=0)

# On the main page -- data set filters
tab1, tab2 = st.tabs(["Time", "Threshold"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:    
        starting_year = st.slider('Starting year', 1900, 2021, 1971)
    with col2:
        ending_year = st.slider('Ending year', starting_year, 2021, 2017)
    with col3:
        time_frequency = st.selectbox('Time frequency', ("annual", "monthly"), index=0)

with tab2:
    col1, col2, col3 = st.columns(3)
    with col1:    
        threshold_dummy = st.selectbox('Threshold dummy', ("True", "False"), index=1)

    with col2:
        threshold_kind = st.selectbox('Threshold kind', ("percentile", "absolute"), index=0)

    with col3:
        threshold = st.number_input('Threshold', value = 90)


# Start consistency routine
stop = False

# Check time consistency for each source
if source == 'CRU TS':
  min_year = 1901
  max_year = 2020
  if starting_year < min_year or ending_year > max_year:
    st.warning('Warning: ' + source + ' data is available from ' + str(min_year) + ' until ' + str(max_year) + ' -- Please select an appropriate time window!', icon="⚠️")
    stop = True
  else:
    source = 'cru'

elif source == 'ERA5':
  min_year = 1979
  max_year = 2021
  if starting_year < min_year or ending_year > max_year:
    st.warning('Warning: ' + source + ' data is available from ' + str(min_year) + ' until ' + str(max_year) + ' -- Please select an appropriate time window!', icon="⚠️")
    stop = True
  else:
    source = 'era'

elif source == 'CSIC':
  min_year = 1901
  max_year = 2020
  if starting_year < min_year or ending_year > max_year:
    st.warning('Warning: ' + source + ' data is available from ' + str(min_year) + ' until ' + str(max_year) + ' -- Please select an appropriate time window!', icon="⚠️")
    stop = True
  else:
    source = 'spei'

else: # (UDelaware)
  min_year = 1900
  max_year = 2017
  if starting_year < min_year or ending_year > max_year:
    st.warning('Warning: ' + source + ' data is available from ' + str(min_year) + ' until ' + str(max_year) + ' -- Please select an appropriate time window!', icon="⚠️")
    stop = True
  else:
    source = 'dela'

# Rename variables as to match datasets names
if variable == 'temperature':
  variable = 'tmp'
elif variable == 'precipitation':
  variable = 'pre'
else:
  variable = 'spei'

# Introduce string for weights
if weight == 'unweighted':
  weight = '_un'
elif weight == 'night lights 2008':
  weight = '_lights'
else:
  weight = ''

## SPEI is not provided annually
if (variable == 'spei' and time_frequency == 'annual'):
  stop = True
  st.warning('Error: variable SPEI is only provided at monthly frequency', icon="⚠️")

## Threshold returns only results for years, not months
if (threshold_dummy == 'True' and time_frequency == 'monthly'):
  stop = True
  st.warning('Error: threshold variables are only provided at annual frequency', icon="⚠️")


# Extract data if consistency checks were passed
if stop == False:
  # Read data from GitHub
  data = pd.read_csv('https://raw.githubusercontent.com/testalorenzo/climate_repository/main/data/'+ geo_resolution + '_' + source + '_' + variable + weight +'.csv', encoding='latin-1')

  # Introduce gaps to fix columns
  if geo_resolution == 'gadm1':
    gap = 2
  else:
    gap = 1
  
  # Extract selected years
  data = data.iloc[:, list(range(gap)) + list(range((starting_year-min_year)*12 + gap, (ending_year-min_year)*12 + gap + 12))]

  # Summarize if time frequency is annual
  if time_frequency == 'annual' and threshold_dummy == 'False':
    observations = data.iloc[:, 0:gap]
    if variable == 'pre':
      data = data.iloc[:, gap:]
      data = data.groupby(np.arange(data.shape[1])//12, axis=1).sum()
    elif variable == 'tmp':
      data = data.iloc[:, gap:]
      data = data.groupby(np.arange(data.shape[1])//12, axis=1).mean()
    data.columns = list(range(starting_year, ending_year + 1))
    data = pd.concat([observations, data], axis=1)

  elif time_frequency == 'annual' and threshold_dummy == 'True':
    observations = data.iloc[:, 0:gap]
    data = data.iloc[:, gap:]
    if threshold_kind == 'percentile':
      limit_values = data.quantile(q=threshold/100, axis=1)
    else:
      limit_values = threshold
    months_over_threshold = data.gt(limit_values, axis=0)
    n_months_over_threshold = months_over_threshold.groupby(np.arange(data.shape[1])//12, axis=1).sum()
    n_months_over_threshold.columns = list(range(starting_year, ending_year + 1))
    data = pd.concat([observations, n_months_over_threshold], axis=1)

  data2 = data.iloc[:, gap:]
  data2.index = data.iloc[:, 0:gap]
  st.line_chart(data2.T)

  col1, col2, col3 = st.columns(3)
  with col1:    
    download_format = st.selectbox('Download format', ("Wide", "Long"), index=0)
    if download_format == 'Long':
      if geo_resolution == 'gadm0':
        data = pd.melt(data, id_vars='iso3', var_name='time', value_name=variable)
      elif geo_resolution == 'gadm1':
        data = pd.melt(data, id_vars=['ID_0', 'NAME_1'], var_name='time', value_name=variable)

  with col2:
    download_extension = st.selectbox('Download extension', ("csv", "json"), index=0)
    if download_extension == 'csv':
      data = data.to_csv().encode('utf-8')
    elif download_extension == 'json':
      data = data.to_json().encode('utf-8')

  with col3:
    st.download_button(
     label="Download data",
     data=data,
     file_name= geo_resolution + '_' + source + '_' + variable + weight + '_data.' + download_extension)