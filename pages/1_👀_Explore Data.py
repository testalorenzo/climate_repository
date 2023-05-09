# ----------------- #
# Visualization tab #
# ----------------- #

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import json


@st.cache_data()
def load_data(geo_resolution, variable, source, weight, weight_year, col_range, row_range):
    """
    Load data from the repository and return a pandas dataframe

    Parameters:
    geo_resolution (str): Geographical resolution of the data
    variable (str): Climate variable of interest
    source (str): Source of the data
    weight (str): Weighting variable
    weight_year (str): Year of the weighting variable

    Returns:
    imported_data (pandas dataframe): Dataframe containing the data
    """
    if weight != "_un":
        link = 'https://raw.githubusercontent.com/testalorenzo/climate_repository/main/data/'+ geo_resolution + '_' + source + '_' + variable + weight + '_' + weight_year + '.csv'
    else:
        link = 'https://raw.githubusercontent.com/testalorenzo/climate_repository/main/data/'+ geo_resolution + '_' + source + '_' + variable + weight + '.csv'
    imported_data = pd.read_csv(link, iterator = True, chunksize = 1000, encoding = 'latin-1', usecols = col_range, skiprows = row_range)
    imported_data = pd.concat(imported_data, ignore_index=True)
    return imported_data

@st.cache_data()
def load_shapes(geo_resolution):
    """
    Load shapefiles from the repository and return a geopandas dataframe

    Parameters:
    geo_resolution (str): Geographical resolution of the data

    Returns:
    world (geopandas dataframe): Geopandas dataframe containing the gadm0 shapes
    """
    if geo_resolution == 'gadm0':
        world = gpd.read_file('https://github.com/testalorenzo/climate_repository/blob/main/poly/simplified_gadm0.gpkg?raw=true')
        world.index = world.GID_0
        world_json = world.to_json()
        world_json = json.loads(world_json)
    else:
        world = gpd.read_file('https://github.com/testalorenzo/climate_repository/blob/main/poly/simplified_gadm1.gpkg?raw=true')
        world.index = world.NAME_1
        world_json = world.to_json()
        world_json = json.loads(world_json)
    return world.reset_index(drop=True), world_json

@st.cache_data()
def load_country_list():
    """
    Load country list from the repository and return a pandas dataframe

    Returns:
    country_list (pandas dataframe): Dataframe containing the country list
    """
    country_list = pd.read_csv('https://github.com/testalorenzo/climate_repository/blob/main/poly/country_list.csv?raw=true')
    return country_list

# Page title
st.set_page_config(page_title="Weighted Climate Data Repository", page_icon="🌎")
st.markdown("# The Weighted Climate Data Repository")
st.markdown("## Explore Data")

# ---------- #
# Parameters #
# ---------- #

# Page structure
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

# Threshold settings
if variable != 'SPEI':
    col1, col2, col3 = st.columns(3)
    # Activate threshold customization
    with col1:
        threshold_dummy = st.selectbox('Threshold', ("True", "False"), index=1, help='Activate threshold customization')
    # Threshold customization
    if threshold_dummy == "True":
        with col2:
            threshold_kind = st.selectbox('Threshold type', ("percentile", "absolute"), index=0, help='Type of threshold specification')
        with col3:
            threshold = st.number_input('Threshold', value = 90, help='Threshold value')
    else:
        threshold_kind = "percentile"
        threshold = 90
else:
    st.caption("Threshold")
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
    time_frequency = st.selectbox('Time frequency', ("yearly", "monthly"), index = 0, help = 'Time frequency of the data')

# Time period, threshold and observations
if source == 'CRU TS':
    min_year = 1901
    max_year = 2022
    source = 'cru'
elif source == 'ERA5':
    min_year = 1940
    max_year = 2022
    source = 'era'
elif source == 'CSIC':
    min_year = 1901
    max_year = 2020
    source = 'spei'
else: # (UDelaware)
    min_year = 1900
    max_year = 2017
    source = 'dela'

col1, col2 = st.columns(2)
# Starting year
with col1:
    starting_year = st.slider('Starting year', min_year, max_year, min_year)
# Ending year
with col2:
    ending_year = st.slider('Ending year', starting_year, max_year, max_year)

# ---------------- #
# Data preparation #
# ---------------- #

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

# Introduce gaps to fix columns
if geo_resolution == 'gadm1':
    gap = 2
else:
    gap = 1

# Extract selected years
col_range = list(range(gap)) + list(range((starting_year - min_year) * 12 + gap, (ending_year - min_year) * 12 + gap + 12))

# Observation filters
world0 = load_country_list()
# observation_list = list(set((data.iloc[:, 0].values).tolist()))
observation_list = world0.COUNTRY.unique().tolist()
observation_list.sort()
options = st.multiselect('Countries', ['ALL'] + observation_list, default='United States', help = 'Choose the geographical units to show in the plot')

# Build row range
world, world_json = load_shapes(geo_resolution)
if 'ALL' in options:
    row_range = []
else:
    opts = world0.loc[world0.COUNTRY.isin(options), 'GID_0'].tolist()
    row_range = list(world[~world['GID_0'].isin(opts)].index) + [0]
    row_range = list(map(lambda x: x + 1, row_range))
    row_range.pop(0)

# Read data from GitHub
data = load_data(geo_resolution, variable, source, weight, weight_year, col_range, row_range)

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

tab1, tab2 = st.tabs(['Time series', 'Choropleth map'])

# ---------------- #
# Plot time series #
# ---------------- #

with tab1: 
    data_plot = data.iloc[:, gap:]
    data_plot.index = data.iloc[:, 0:gap]
    if time_frequency == 'monthly':
        label_vector = [str(x) + "_" + str(y) for x in range(starting_year, ending_year + 1) for y in range(1,13)]
        label_vector = pd.to_datetime(label_vector, format="%Y_%m")
    else:
        label_vector = data_plot.columns
        label_vector = pd.to_datetime(label_vector, format="%Y")
    data_plot.columns = label_vector
    data_plot = data_plot.reset_index()
    if geo_resolution == 'gadm0':
        data_plot = pd.melt(data_plot, id_vars='index', var_name='time', value_name=variable)
    else:
        data_plot = pd.melt(data_plot, id_vars='index', var_name='time', value_name=variable)

    # Plot settings
    alt.themes.enable("streamlit")

    highlight = alt.selection(type='single', on='mouseover', fields=['index'], nearest=True)

    base = alt.Chart(data_plot).encode(
        x=alt.X('time'),
        y=alt.Y(variable),
        color=alt.Color('index', scale=alt.Scale(scheme='viridis')))

    points = base.mark_circle().encode(
        opacity=alt.value(0),
        tooltip=[
            alt.Tooltip('time', title='time'),
            alt.Tooltip(variable, title=variable),
            alt.Tooltip('index', title='index')
        ]).add_selection(highlight)

    # lines = base.mark_line().encode(size=alt.condition(~highlight, alt.value(1), alt.value(3)))
    lines = base.mark_line().encode(size=alt.value(1.5))

    ts_plot = (points + lines).interactive()

    st.altair_chart(ts_plot, use_container_width=True)

# ------------------- #
# Plot choropleth map #
# ------------------- #

with tab2: 
    snapshot = st.slider('Snapshot year', starting_year, ending_year, starting_year, 1, help = 'Choose the year to show in the plot')
    if geo_resolution == 'gadm0':
        snapshot_data = world.merge(data, left_on='GID_0', right_on='iso3')
        # snapshot_data = pd.melt(snapshot_data, id_vars=['iso3', 'geometry'])
    else:
        snapshot_data = world.loc[:,['GID_0', 'NAME_1', 'geometry']].merge(data, on=['GID_0', 'NAME_1'])
        # snapshot_data = pd.melt(snapshot_data, id_vars=['ID_0', 'NAME_1', 'geometry'])

    if options == []:
        st.warning('No country selected')
    else:
        fig = px.choropleth_mapbox(snapshot_data, geojson=snapshot_data.geometry, locations=snapshot_data.index, color = int(snapshot), #color='value', animation_frame="variable",
                                   color_continuous_scale="Viridis", mapbox_style="carto-positron", zoom=1, opacity=0.5)
    st.plotly_chart(fig, use_container_width=True)

# Side bar images
# st.sidebar.image("Embeds logo.png", use_column_width=True)
# st.sidebar.image("download.jpeg", use_column_width=True)
with st.sidebar:
    """
    [Institute of Economics](https://www.santannapisa.it/en/istituto/economia) and [L'EMbeDS Department](https://www.santannapisa.it/en/department-excellence/embeds)

    Sant'Anna School of Advanced Studies (Pisa, Italy)
    """