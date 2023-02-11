# ----------------- #
# Visualization tab #
# ----------------- #

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
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

# 1. Select the kind of graphical representation
plot1, plot2 = st.tabs(["Time series", "Choropleth map"])

# Time series plot
with plot1:

    # 2.a Select the geographical resolution, the climate variable, the variable source, the weighting scheme, the weighting year, threshold settings and time frequency

    # Filter structure
    col1, col2, col3, col4, col5 = st.columns([1,1,1.3,1,1])

   # Climate variable
    with col1:
        variable = st.selectbox('Climate variable', ("temperature", "precipitation", "SPEI"), index=0, help='Measured climate variable of interest', key = 'variable_ts')
    # Variable source
    if variable != "SPEI":
        with col2:
            source = st.selectbox('Variable source', ("CRU TS", "ERA5", "UDelaware"), index=0, help='Source of data for the selected climate variable', key = 'source_ts')
    else:
        with col2:
            source = "CSIC"
            st.caption("Variable source")
            st.markdown(source)
    # Geographical resolution
    with col3:
        geo_resolution = st.selectbox('Geographical resolution', ('gadm0', 'gadm1'), index=0, help='Geographical units of observation', key = 'geo_resolution_ts')
    # Weighting scheme
    with col4:
        weight = st.selectbox('Weighting type', ('population density', 'night lights', 'unweighted'), index=0, help='Weighting scheme specification', key = 'weight_ts')
    # Weighting year
    if weight!="unweighted":
        with col5:
            weight_year = st.selectbox('Weighting year', ('2000', '2005', '2010', '2015'), index=0, help='Base year for the weighting scheme', key = 'weight_year_ts')
    else:
        weight_year = "NA"
    # Threshold settings
    if variable != 'SPEI':
        col1, col2, col3 = st.columns(3)
        # Activate threshold customization
        with col1:
            threshold_dummy = st.selectbox('Threshold dummy', ("True", "False"), index=1, help='Activate threshold customization', key = 'threshold_dummy_ts')
        # Threshold customization
        if threshold_dummy == "True":
            with col2:
                threshold_kind = st.selectbox('Threshold type', ("percentile", "absolute"), index=0, help='Type of threshold specification', key = 'threshold_kind_ts')
            with col3:
                threshold = st.number_input('Threshold', value = 90, help='Threshold value', key = 'threshold_ts')
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
        time_frequency = 'yearly'
        st.caption('Time frequency')
        st.markdown(time_frequency)
    else:
        time_frequency = st.selectbox('Time frequency', ("yearly", "monthly"), index=0, help='Time frequency of the data', key = 'time_frequency_ts')


    # 2.b Select the time period, the threshold and observations.

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

    # Preferences structure
    tab1, tab3 = st.tabs(["Time", "Observations"])

    # Time preferences
    with tab1:
        col1, col2 = st.columns(2)
        # Starting year
        with col1:
            starting_year = st.slider('Starting year', min_year, max_year, min_year)
        # Ending year
        with col2:
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


# 3. Access data for time series

# Read data from GitHub
data = load_data(geo_resolution, variable, source, weight, weight_year)

# Introduce gaps to fix columns
if geo_resolution == 'gadm1':
    gap = 2
else:
    gap = 1

# Extract selected years
data = data.iloc[:, list(range(gap)) + list(range((starting_year - min_year) * 12 + gap, (ending_year - min_year) * 12 + gap + 12))]

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

# Observation filters
with tab3:
    observation_list = list(set((data.iloc[:, 0].values).tolist()))
    options = st.multiselect('Select specific units of observations', observation_list + ['ALL'], 'ALL')

with plot1:
    
    # 6.1 Plot time series

    data_plot = data.iloc[:, gap:]
    data_plot.index = data.iloc[:, 0:gap]
    if 'ALL' in options:
        mask = pd.Series([True] * len(data_plot.index))
    else:
        mask = pd.Series(data_plot.index).apply(lambda x: x[0]).isin(options) 
    mask.index = data_plot.index
    data_plot = data_plot.loc[mask, :]
    if time_frequency == 'monthly':
        label_vector = [str(x) + "_" + str(y) for x in range(starting_year, ending_year + 1) for y in range(1,13)]
        label_vector = pd.to_datetime(label_vector, format="%Y_%m")
    else:
        label_vector = data_plot.columns
        label_vector = pd.to_datetime(label_vector, format="%Y")
    data_plot.columns = label_vector

    # Plot settings
    alt.themes.enable("streamlit")
    st.line_chart(data_plot.T)


# Map snapshot
with plot2:

    # 2.b Select the geographical resolution, the climate variable, the variable source, the weighting scheme, the weighting year, threshold settings and time frequency

    # Filter structure
    col1, col2, col3, col4, col5 = st.columns([1,1,1.3,1,1])

    # Climate variable
    with col1:
        variable2 = st.selectbox('Climate variable', ("temperature", "precipitation"), index=0, help='Measured climate variable of interest')
    # Variable source
    with col2:
        source2 = st.selectbox('Variable source', ("CRU TS", "ERA5", "UDelaware"), index=0, help='Source of data for the selected climate variable')
    # Geographical resolution
    with col3:
        geo_resolution2 = "gadm0"
        st.caption('Geographical resolution')
        st.markdown(geo_resolution2)
    # Weighting scheme
    with col4:
        weight2 = st.selectbox('Weighting type', ('population density', 'night lights', 'unweighted'), index=0, help='Weighting scheme specification')
    # Weighting year
    if weight2 != "unweighted":
        with col5:
            weight_year2 = st.selectbox('Weighting year', ('2000', '2005', '2010', '2015'), index=0, help='Base year for the weighting scheme')
    else:
        weight_year2 = "NA"
    # Threshold settings
    col1, col2, col3 = st.columns(3)
    # Activate threshold customization
    with col1:
        threshold_dummy2 = st.selectbox('Threshold dummy', ("True", "False"), index=1)
    # Threshold customization
    if threshold_dummy2 == "True":
        with col2:
            threshold_kind2 = st.selectbox('Threshold type', ("percentile", "absolute"), index=0)
        with col3:
            threshold2 = st.number_input('Threshold', value = 90)
    else:
        threshold_kind2 = "percentile"
        threshold2 = 90

    # Time frequency
    time_frequency2 = 'yearly'
    st.caption('Time frequency')
    st.markdown(time_frequency2)


    # 2.b Select the time snapshot

    if source2 == 'CRU TS':
        min_year2 = 1901
        max_year2 = 2020
        source2 = 'cru'
    elif source2 == 'ERA5':
        min_year2 = 1979
        max_year2 = 2021
        source2 = 'era'
    elif source2 == 'CSIC':
        min_year2 = 1901
        max_year2 = 2020
        source2 = 'spei'
    else: # (UDelaware)
        min_year2 = 1900
        max_year2 = 2017
        source2 = 'dela'

    snapshot = st.slider('Snapshot year', min_value = min_year2, max_value = max_year2, value = min_year2)


# Rename variables as to match datasets names
if variable2 == 'temperature':
    variable2 = 'tmp'
elif variable2 == 'precipitation':
    variable2 = 'pre'
else:
    variable2 = 'spei'

# Introduce string for weights
if weight2 == 'unweighted':
    weight2 = '_un'
elif weight2 == 'night lights':
    weight2 = '_lights'
else:
    weight2 = ''

# 3. Access data for map

# Read data from GitHub
data2 = load_data(geo_resolution2, variable2, source2, weight2, weight_year2)

# Introduce gaps to fix columns
gap2 = 1

# Extract selected years
data2 = data2.iloc[:, list(range(gap2)) + list(range((snapshot - min_year2) * 12 + gap2, (snapshot - min_year2) * 12 + gap2 + 12))]

# Summarize if time frequency is yearly
if time_frequency2 == 'yearly' and threshold_dummy2 == 'False':
    observations2 = data2.iloc[:, 0:gap2]
    if variable2 == 'pre':
        data2 = data2.iloc[:, gap2:]
        data2 = data2.groupby(np.arange(data2.shape[1])//12, axis=1).sum()
    elif variable2 == 'tmp':
        data2 = data2.iloc[:, gap2:]
        # days_by_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 31, 31]
        data2 = data2.groupby(np.arange(data2.shape[1])//12, axis=1).mean()
    data2.columns = list(range(snapshot, snapshot + 1))
    data2 = pd.concat([observations2, data2], axis=1)

elif time_frequency2 == 'yearly' and threshold_dummy2 == 'True':
    observations2 = data2.iloc[:, 0:gap2]
    data2 = data2.iloc[:, gap2:]
    if threshold_kind2 == 'percentile':
        limit_values2 = data2.quantile(q=threshold2/100, axis=1)
    else:
        limit_values2 = threshold2
    months_over_threshold2 = data2.gt(limit_values2, axis=0)
    n_months_over_threshold2 = months_over_threshold2.groupby(np.arange(data2.shape[1])//12, axis=1).sum()
    n_months_over_threshold2.columns = list(range(snapshot, snapshot + 1))
    data2 = pd.concat([observations2, n_months_over_threshold2], axis=1)

with plot2:
    
    # 6.2 Plot map
    
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    fig, ax = plt.subplots(1, 1)
    snapshot_data = data2
    snapshot_data.columns = ['iso_a3', 'to_plot']
    snapshot_data = world.merge(snapshot_data, on='iso_a3')
    #snapshot_data = pd.merge(snapshot_data, world, left_on='iso3', right_on='iso_a3')
    #st.dataframe(data=snapshot_data)
    snapshot_data.plot(column='to_plot', ax=ax, legend=True, legend_kwds={'label': str(variable2) + " by Country in " + str(snapshot), 'orientation': "horizontal"})
    st.pyplot(fig=fig)


# Side bar images
st.sidebar.image("Embeds logo.png", use_column_width=True)
st.sidebar.image("download.jpeg", use_column_width=True)