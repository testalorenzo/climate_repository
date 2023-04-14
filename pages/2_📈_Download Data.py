# ------------ #
# Download tab #
# ------------ #

import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data()
def load_data(geo_resolution, variable, source, weight, weight_year):
    if weight != "_un":
        data = pd.read_csv('https://raw.githubusercontent.com/testalorenzo/climate_repository/main/data/'+ geo_resolution + '_' + source + '_' + variable + weight + '_' + weight_year + '.csv', encoding='latin-1')
    else:
        data = pd.read_csv('https://raw.githubusercontent.com/testalorenzo/climate_repository/main/data/'+ geo_resolution + '_' + source + '_' + variable + weight +'.csv', encoding='latin-1')
    return data


# Page title
st.set_page_config(page_title="Weighted Climate Data Repository", page_icon="🌎", initial_sidebar_state="expanded")
st.markdown("# The Weighted Climate Data Repository")
st.markdown("## Download Data")


# 1. Select the geographical resolution, the climate variable, the variable source, the weighting scheme and the weighting year.

# Filter structure
col1, col2, col3, col4, col5 = st.columns([1,1,1.3,1.1,1])

# Climate variable
with col1:
    variable = st.selectbox('Climate variable', ("temperature", "precipitation", "SPEI"), index=0, help='Measured climate variable of interest')
# Variable source
if variable != "SPEI":
    with col2:
        source = st.selectbox('Variable source', ("CRU TS", "ERA5", "UDelaware"), index=0, help='Source of data for the selected climate variable')
else:
    with col2:
        source = "CSIC"
        st.caption("Variable source")
        st.markdown(source)
# Geographical resolution
with col3:
    geo_resolution = st.selectbox('Geographical resolution', ('gadm0', 'gadm1'), index=0, help='Geographical units of observation')
# Weighting scheme
with col4:
    weight = st.selectbox('Weighting variable', ('population density', 'night lights', 'unweighted'), index=0, help='Weighting variable specification')
# Weighting year
if weight!="unweighted":
    with col5:
        weight_year = st.selectbox('Weighting year', ('2000', '2005', '2010', '2015'), index=0, help='Base year for the weighting variable')
else:
    weight_year = "NA"

# 2. Select the time period, the threshold and observations.

# Threshold settings
if variable != 'SPEI':
    col1, col2, col3 = st.columns(3)
    # Activate threshold customization
    with col1:    
        threshold_dummy = st.selectbox('Threshold', ("True", "False"), index=1)
    # Threshold customization
    if threshold_dummy == "True":
        with col2:
            threshold_kind = st.selectbox('Threshold type', ("percentile", "absolute"), index=0)
        with col3:
            threshold = st.number_input('Threshold', value = 90)
    else:
        threshold_kind = "percentile"
        threshold = 90
else:
    st.warning('Warning: ' + variable + ' data do not allow for threshold customization' , icon="⚠️")


# Time period, threshold and observations.

if source == 'CRU TS':
    min_year = 1901
    max_year = 2020
    source = 'cru'
elif source == 'ERA5':
    min_year = 1979
    max_year = 2021
    source = 'era'
elif source == 'CSIC':
    min_year = 1901
    max_year = 2020
    source = 'spei'
else: # (UDelaware)
    min_year = 1900
    max_year = 2017
    source = 'dela'


# 3. Preferences structure

# Time preferences
col1, col2, col3 = st.columns(3)
# Frequency
with col1:
    if variable == 'SPEI':
        time_frequency = 'monthly'
        st.caption('Time frequency')
        st.markdown(time_frequency)
    elif threshold_dummy == 'True':
        time_frequency = 'yearly'
        st.caption('Time frequency')
        st.markdown(time_frequency)
    else:
        time_frequency = st.selectbox('Time frequency', ("yearly", "monthly"), index = 0, help = 'Time frequency of the data', key = 'time_frequency_ts')
# Starting year
with col2:
    starting_year = st.slider('Starting year', min_year, max_year, min_year)
# Ending year
with col3:
    ending_year = st.slider('Ending year', starting_year, max_year, max_year)

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
elif weight == 'night lights':
    weight = '_lights'
else:
    weight = ''


# 4. Access data

# Read data from GitHub
data = load_data(geo_resolution, variable, source, weight, weight_year)

# Introduce gaps to fix columns
if geo_resolution == 'gadm1':
    gap = 2
else:
    gap = 1

# Extract selected years
data = data.iloc[:, list(range(gap)) + list(range((starting_year-min_year)*12 + gap, (ending_year-min_year)*12 + gap + 12))]

# Summarize if time frequency is yearly
if time_frequency == 'yearly' and threshold_dummy == 'False':
    observations = data.iloc[:, 0:gap]
    if variable == 'pre':
        data = data.iloc[:, gap:]
        data = data.groupby(np.arange(data.shape[1])//12, axis=1).sum()
    elif variable == 'tmp':
        data = data.iloc[:, gap:]
        # days_by_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 31, 31]
        data = data.groupby(np.arange(data.shape[1])//12, axis=1).mean()
    data.columns = list(range(starting_year, ending_year + 1))
    data = pd.concat([observations, data], axis=1)

elif time_frequency == 'yearly' and threshold_dummy == 'True':
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


# 5. Download data

col1, col2, col3 = st.columns(3)

with col1:    
	download_format = st.selectbox('Download format', ("Wide", "Long"), index=0)
	if download_format == 'Long':
		if geo_resolution == 'gadm0':
			data = pd.melt(data, id_vars='iso3', var_name='time', value_name=variable)
		elif geo_resolution == 'gadm1':
			data = pd.melt(data, id_vars=['ID_0', 'NAME_1'], var_name='time', value_name=variable)

data_show = data

with col2:
	download_extension = st.selectbox('Download extension', ("csv", "json"), index=0)
	if download_extension == 'csv':
		data = data.to_csv().encode('utf-8')
	elif download_extension == 'json':
		data = data.to_json().encode('utf-8')

with col3:
    st.download_button(label = "Download data", data = data, file_name = geo_resolution + '_' + source + '_' + variable + weight + '_data.' + download_extension)
with col3:
    meta_text = 'Metadata\n' + 'Geographic resolution: ' + geo_resolution + '\nClimate variable source: ' + source + '\nClimate variable: ' + variable + '\nWeighting variable: ' + weight + '\nWeighting base year: '+ str(weight_year) + '\n\nRemember to cite our work!\nhttps://climaterepo.streamlit.app/'
    st.download_button(label="Download metadata", data = meta_text, file_name= 'metadata.txt')

# 6. Visualize data
st.markdown('### Preview of the data')
st.dataframe(data_show)

# Side bar images
# st.sidebar.image("Embeds logo.png", use_column_width=True)
# st.sidebar.image("download.jpeg", use_column_width=True)
with st.sidebar:
    """
    [Institute of Economics](https://www.santannapisa.it/en/istituto/economia) and [L'EMbeDS Department](https://www.santannapisa.it/en/department-excellence/embeds)
    
    Sant'Anna School of Advanced Studies (Pisa, Italy)
    """