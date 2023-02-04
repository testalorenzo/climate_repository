# ----------------- #
# Visualization tab #
# ----------------- #

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import vega_datasets
import geopandas as gpd
import matplotlib.pyplot as plt

@st.cache
def load_data(geo_resolution, variable, source, weight, weight_year):
    if weight != "_un":
        imported_data = pd.read_csv('https://raw.githubusercontent.com/testalorenzo/climate_repository/main/data/'+ geo_resolution + '_' + source + '_' + variable + weight + '_' + weight_year + '.csv', encoding='latin-1')
    else:
        imported_data = pd.read_csv('https://raw.githubusercontent.com/testalorenzo/climate_repository/main/data/'+ geo_resolution + '_' + source + '_' + variable + weight +'.csv', encoding='latin-1')
    return imported_data

# Page title
st.markdown("# Explore Data")


# 1. Select the geographical resolution, the climate variable, the variable source, the weighting scheme, the weighting year, threshold settings and time frequency

# Filter structure
col1, col2, col3, col4, col5 = st.columns([1.3,1,1,1,1])

# Geographical resolution
with col1:
    geo_resolution = st.selectbox('Geographical resolution', ('gadm0', 'gadm1'), index=0, help='Geographical units of observation')
# Climate variable
with col2:
    variable = st.selectbox('Climate variable', ("temperature", "precipitation", "SPEI"), index=0, help='Measured climate variable of interest')
# Variable source
if variable != "SPEI":
    with col3:
        source = st.selectbox('Variable source', ("CRU TS", "ERA5", "UDelaware"), index=0, help='Source of data for the selected climate variable')
else:
    with col3:
        source = "CSIC"
        st.caption("Variable source")
        st.markdown(source)
# Weighting scheme
with col4:
    weight = st.selectbox('Weighting type', ('population density', 'night lights', 'unweighted'), index=0, help='Weighting scheme specification')
# Weighting year
if weight!="unweighted":
    with col5:
        weight_year = st.selectbox('Weighting year', ('2000', '2005', '2010', '2015'), index=0, help='Base year for the weighting scheme')

# Threshold settings
if variable != 'SPEI':
    col1, col2, col3 = st.columns(3)
    # Activate threshold customization
    with col1:    
        threshold_dummy = st.selectbox('Threshold dummy', ("True", "False"), index=1)
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
    st.caption("Threshold dummy")
    st.markdown("False")

# Time frequency
if variable == 'SPEI':
    time_frequency = 'monthly'
    st.caption('Time frequency')
    st.markdown(time_frequency)
elif threshold_dummy == 'True':
    time_frequency = 'annual'
    st.caption('Time frequency')
    st.markdown(time_frequency)
else:
    time_frequency = st.selectbox('Time frequency', ("annual", "monthly"), index=0)


# 2. Select the kind of graphical representation

plot1, plot2 = st.tabs(["Time series", "Choropleth map"])

# Time series plot
with plot1:

    # 3. Select the time period, the threshold and observations.

    # Preferences structure
    tab1, tab3 = st.tabs(["Time", "Observations"])

    # Time preferences
    with tab1:
        col1, col2 = st.columns(2)
        # Starting year
        with col1:    
            starting_year = st.slider('Starting year', 1900, 2021, 1971)
        # Ending year
        with col2:
            ending_year = st.slider('Ending year', starting_year, 2021, 2017)
   


# 4. Consistency routine

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
elif weight == 'night lights':
    weight = '_lights'
else:
    weight = ''

    
# Map snapshot
with plot2:

    # 3. Select snapshot
    st.markdown("Snapshot")
    snapshot = st.slider('Snapshot year', min_year, max_year, 1971)

    
# 5. Access data

# Extract data if consistency checks were passed
if stop is False:
    # Read data from GitHub
    data = load_data(geo_resolution, variable, source, weight, weight_year)

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
            # days_by_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 31, 31]
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

    # Observation filters
    with tab3:
        observation_list = list(set((data.iloc[:, 0].values).tolist()))
        options = st.multiselect('Select specific units of observations', observation_list + ['ALL'], 'ALL')

    with plot1:
        
        # 6.1 Plot time series

        data2 = data.iloc[:, gap:]
        data2.index = data.iloc[:, 0:gap]
        if 'ALL' in options:
            mask = pd.Series([True] * len(data2.index))
        else:
            mask = pd.Series(data2.index).apply(lambda x: x[0]).isin(options) 
        mask.index = data2.index
        data2 = data2.loc[mask, :]
        if time_frequency == 'monthly':
            label_vector = [str(x) + "_" + str(y) for x in range(starting_year, ending_year + 1) for y in range(1,13)]
            label_vector = pd.to_datetime(label_vector, format="%Y_%m")
        else:
            label_vector = data2.columns
            label_vector = pd.to_datetime(label_vector, format="%Y")
        data2.columns = label_vector

        # Plot settings
        alt.themes.enable("streamlit")
        st.line_chart(data2.T)

    with plot2:
        
        # 6.2 Plot map
       
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        fig, ax = plt.subplots(1, 1)
        world.plot(column='pop_est', ax=ax, legend=True, legend_kwds={'label': str(variable) + " by Country in " + str(snapshot), 'orientation': "horizontal"})
        st.pyplot(fig=fig)


# Side bar images
st.sidebar.image("Embeds logo.png", use_column_width=True)
st.sidebar.image("download.jpeg", use_column_width=True)
