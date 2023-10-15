# ----------------- #
# Visualization tab #
# ----------------- #

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import duckdb as db
import pickle
import datetime

# --------------------- #
# Initial Session State #
# --------------------- #

if "initialized" not in st.session_state:
    st.session_state['initialized'] = True
    st.session_state['variable'] = 'temperature'
    st.session_state['source'] = 'CRU TS'
    st.session_state['geo_resolution'] = 'gadm0'
    st.session_state['weight'] = 'population density'
    st.session_state['weight_year'] = '2015'
    st.session_state['threshold_dummy'] = 'False'
    st.session_state['threshold_kind'] = 'percentile'
    st.session_state['threshold'] = 90
    st.session_state['time_frequency'] = 'yearly'
    st.session_state['starting_year'] = 1901
    st.session_state['ending_year'] = 2022
    st.session_state['row_range'] = tuple(['USA'])

# ------------ #
# Data imports #
# ------------ #

@st.cache_data(ttl=3600, show_spinner="Fetching data...")
def load_data(geo_resolution, variable, source, weight, weight_year, col_range, row_range, time_frequency, threshold_dummy):
    if weight != "_un":
        file = './data/' + geo_resolution + '_' + source + '_' + variable + weight + '_' + weight_year + '.parquet'
    
    else:
        file = './data/' + geo_resolution + '_' + source + '_' + variable + weight + '.parquet'

    if time_frequency == 'daily' or threshold_dummy == "True":
        file = './data/' + geo_resolution + '_' + source + '_' + variable + '_' + weight_year + '_daily.parquet'

    if geo_resolution == 'gadm0':
        country_name = 'iso3'
    else:
        country_name = 'GID_0'

    query = f"SELECT {col_range} FROM '{file}' WHERE {country_name} IN {row_range}"
    imported_data = db.query(query).df()
    return imported_data

@st.cache_data(ttl=3600, show_spinner="Fetching shapes...")
def load_shapes(geo_resolution):
    """
    Load shapefiles from the repository and return a geopandas dataframe

    Parameters:
    geo_resolution (str): Geographical resolution of the data

    Returns:
    world (geopandas dataframe): Geopandas dataframe containing the gadm0 shapes
    """
    if geo_resolution == 'gadm0':
        layer = '0'
        idx_name = 'GID_0'
    else:
        layer = '1'
        idx_name = 'NAME_1'

    picklefile = open('./poly/gadm' + layer + '.pickle', 'rb')
    shapes = pickle.load(picklefile)
    shapes.index = shapes[idx_name]
    picklefile.close()
    return shapes.reset_index(drop=True)

@st.cache_data(ttl=3600, show_spinner="Fetching country names...")
def load_country_list():
    """
    Load country list from the repository and return a pandas dataframe

    Returns:
    country_list (pandas dataframe): Dataframe containing the country list
    """
    country_list = pd.read_csv('./poly/country_list.csv')
    return country_list

# ------------- #
# Page settings #
# ------------- #

st.set_page_config(page_title="Weighted Climate Data Repository", page_icon="🌎")

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """

st.markdown(hide_menu_style, unsafe_allow_html=True)

st.markdown("# The Weighted Climate Data Repository")
st.markdown("## Explore Data")

# ---------- #
# Parameters #
# ---------- #

# Cols
col1, col2, col3, col4, col5 = st.columns([1,1,1.3,1.1,1])
if st.session_state['variable'] != 'SPEI':
    subcol1, subcol2, subcol3 = st.columns([1,1,1])

# Climate variable
with col1:
    st.selectbox('Climate variable', ("temperature", "precipitation", "SPEI"),
                 index=0, help='Measured climate variable of interest', key='variable')

# Variable source
if st.session_state.variable != "SPEI":
    with col2:
        st.selectbox('Variable source', ("CRU TS", "ERA5", "UDelaware"), index=0,
                     help='Source of data for the selected climate variable', key='source')
else:
    with col2:
        st.caption("Variable source")
        st.markdown("CSIC")

# Geographical resolution
with col3:
    st.selectbox('Geographical resolution', ('gadm0', 'gadm1'), index=0,
                 help='Geographical units of observation. gadm0 stands for countries; gadm1 stands for the first administrative level (states, regions, etc.)', key='geo_resolution')

# Weighting scheme
with col4:
    st.selectbox('Weighting variable', ('population density', 'night lights', 'unweighted'), index=0,
                 help='Weighting variable specification', key='weight')

# Weighting year
if st.session_state.weight != "unweighted":
    with col5:
        st.selectbox('Weighting year', ('2000', '2005', '2010', '2015'), index=0,
                    help='Base year for the weighting variable', key='weight_year')

# Threshold settings
if st.session_state.source == 'ERA5' and st.session_state.weight_year == '2015' and st.session_state.geo_resolution == 'gadm0':
    # Activate threshold customization
    with subcol1:
        st.selectbox('Threshold', ("False", "True"),
                     help='Activate threshold customization', key='threshold_dummy')
    # Threshold customization
    if st.session_state.threshold_dummy == "True":
        with subcol2:
            st.selectbox('Threshold type', ("percentile", "absolute"), index=0,
                         help='Type of threshold specification', key='threshold_kind')
        with subcol3:
            st.number_input('Threshold', value = 90, help='Threshold value', key='threshold')
else:
    st.caption("Threshold")
    st.markdown("False")

# Time frequency
if st.session_state.variable == 'SPEI':
    st.session_state.time_frequency = 'monthly'
    st.caption('Time frequency')
    st.markdown("monthly")
elif st.session_state.threshold_dummy == 'True':
    st.selectbox('Time frequency', ("yearly", "monthly"), index = 0, help = 'Time frequency of the data', key='time_frequency')
elif st.session_state.source == 'ERA5' and st.session_state.weight_year == '2015' and st.session_state.geo_resolution == 'gadm0':
    st.selectbox('Time frequency', ("yearly", "monthly", "daily"), index = 0, help = 'Time frequency of the data', key='time_frequency')
else:
    st.selectbox('Time frequency', ("yearly", "monthly"), index = 0, help = 'Time frequency of the data', key='time_frequency')

# Time period, threshold and observations
if st.session_state.source == 'CRU TS':
    min_year = 1901
    max_year = 2022
    source = 'cru'
elif st.session_state.source == 'ERA5':
    if st.session_state.time_frequency == 'daily' or st.session_state.threshold_dummy == 'True':
        min_year = 1950
        max_year = 2023
    else:
        min_year = 1940
        max_year = 2022
    source = 'era'
elif st.session_state.source == 'CSIC':
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
    st.slider('Starting year', min_year, max_year, min_year, key='starting_year')
# Ending year
with col2:
    if st.session_state.time_frequency == 'daily' or st.session_state.threshold_dummy == 'True':
        st.slider('Ending year', st.session_state.starting_year, max_year, st.session_state.starting_year, key='ending_year')
    else:
        st.slider('Ending year', st.session_state.starting_year, max_year, max_year, key='ending_year')

# -------------------- #
# Filters before query #
# -------------------- #

# Rename variables as to match datasets names
if st.session_state.variable == 'temperature':
    variable = 'tmp'
elif st.session_state.variable == 'precipitation':
    variable = 'pre'
else:
    variable = 'spei'

# Introduce string for weights
if st.session_state.weight == 'unweighted':
    weight = '_un'
elif st.session_state.weight == 'night lights':
    weight = '_lights'
else:
    weight = ''

# Introduce gaps to fix columns
if st.session_state.geo_resolution == 'gadm1':
    gap = 2
else:
    gap = 1

# Extract selected years
months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
if st.session_state.geo_resolution == 'gadm0':
    if st.session_state.variable == 'spei':
        col_range = str(['iso3'] + ["w" + y + str(x) for x in range(st.session_state.starting_year, st.session_state.ending_year + 1) for y in months])[1:-1].replace("'", "")
    else:
        col_range = str(['iso3'] + [y + str(x) for x in range(st.session_state.starting_year, st.session_state.ending_year + 1) for y in months])[1:-1].replace("'", "")
    if st.session_state.time_frequency == 'daily' or st.session_state.threshold_dummy == 'True':
        col_range = str(['iso3'] + ['[X' + str(x).replace('-', '') + ']' for x in pd.date_range(start=str(st.session_state.starting_year) + "-01-01",end= str(st.session_state.ending_year) + "-12-31").format("YYYY.MM.DD") if x != ''])[1:-1].replace("'", "")
else:
    if st.session_state.variable == 'spei':
        col_range = str(['GID_0', 'NAME_1'] + ["w" + y + str(x) for x in range(st.session_state.starting_year, st.session_state.ending_year + 1) for y in months])[1:-1].replace("'", "")
    else:
        col_range = str(['GID_0', 'NAME_1'] + [y + str(x) for x in range(st.session_state.starting_year, st.session_state.ending_year + 1) for y in months])[1:-1].replace("'", "")
    # if time_frequency == 'daily':
    #     col_range = str(['GID_0', 'NAME_1'] + ['[X' + str(x).replace('-', '') + ']' for x in pd.date_range(start=str(starting_year) + "-01-01",end= str(ending_year) + "-12-31").format("YYYY.MM.DD") if x != ''])[1:-1].replace("'", "")

# Observation filters
world0 = load_country_list()
observation_list = world0.COUNTRY.unique().tolist()
observation_list.sort()
options = st.multiselect('Countries', ['ALL'] + observation_list, default='United States', help = 'Choose the geographical units to show in the plot')

# Build row range
if 'ALL' in options:
    row_range = tuple(world0.GID_0.tolist())
else:
    row_range = tuple(world0.loc[world0.COUNTRY.isin(options), 'GID_0'].tolist())

st.session_state.row_range = row_range

# --------- #
# Load data #
# --------- #

# Read data from GitHub
data = load_data(st.session_state.geo_resolution, variable, source, weight, st.session_state.weight_year,
                 col_range, st.session_state.row_range, st.session_state.time_frequency, st.session_state.threshold_dummy)

# Fix daily value type
if st.session_state.time_frequency == 'daily' or st.session_state.threshold_dummy == 'True':
    data = data.applymap(lambda x: x[0] if isinstance(x, list) else x)
    data.columns = ['iso3'] + [x for x in pd.date_range(start=str(st.session_state.starting_year) + "-01-01", periods=(data.shape[1]-1)).format("YYYY.MM.DD") if x != '']

# Summarize if time frequency is yearly
if st.session_state.time_frequency == 'yearly' and st.session_state.threshold_dummy == 'False':
    observations = data.iloc[:, 0:gap]
    if variable == 'pre':
        data = data.iloc[:, gap:]
        data = data.groupby(np.arange(data.shape[1])//12, axis=1).sum()
    elif variable == 'tmp':
        data = data.iloc[:, gap:]
        # days_by_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 31, 31]
        data = data.groupby(np.arange(data.shape[1])//12, axis=1).mean()
    data.columns = list(range(st.session_state.starting_year, st.session_state.ending_year + 1))
    data = pd.concat([observations, data], axis=1)
elif st.session_state.threshold_dummy == 'True':
    observations = data.iloc[:, 0:gap]
    data = data.iloc[:, gap:]
    if st.session_state.threshold_kind == 'percentile':
        limit_values = data.quantile(q=st.session_state.threshold/100, axis=1)
    else:
        limit_values = st.session_state.threshold
    days_over_threshold = data.gt(limit_values, axis=0)
    days_over_threshold = days_over_threshold.T
    days_over_threshold.index = pd.to_datetime(days_over_threshold.index)
    if st.session_state.time_frequency == 'yearly':
        n_aggregate_over_threshold = days_over_threshold.groupby(by=[days_over_threshold.index.year]).sum()
        n_aggregate_over_threshold = n_aggregate_over_threshold.T
        n_aggregate_over_threshold.columns = list(range(st.session_state.starting_year, st.session_state.ending_year + 1))
    elif st.session_state.time_frequency == 'monthly':
        n_aggregate_over_threshold = days_over_threshold.groupby(by=[days_over_threshold.index.year, days_over_threshold.index.month]).sum()
        n_aggregate_over_threshold = n_aggregate_over_threshold.T
        n_aggregate_over_threshold.columns = [y + str(x) for x in range(st.session_state.starting_year, st.session_state.ending_year + 1) for y in months]
    data = pd.concat([observations, n_aggregate_over_threshold], axis=1)


# ---------------- #
# Plot time series #
# ---------------- #

tab1, tab2 = st.tabs(['Time series', 'Choropleth map'])

with tab1: 
    data_plot = data.iloc[:, gap:]
    data_plot.index = data.iloc[:, 0:gap]
    if st.session_state.time_frequency == 'monthly':
        label_vector = [str(x) + "_" + str(y) for x in range(st.session_state.starting_year, st.session_state.ending_year + 1) for y in range(1,13)]
        label_vector = pd.to_datetime(label_vector, format="%Y_%m")
    elif st.session_state.time_frequency == 'daily':
        label_vector = [str(x) for x in pd.date_range(start=str(st.session_state.starting_year) + "-01-01",end= str(st.session_state.ending_year) + "-12-31").format("YYYY.MM.DD") if x != '']
        label_vector = pd.to_datetime(label_vector, format="%Y-%m-%d")
    else:
        label_vector = data_plot.columns
        label_vector = pd.to_datetime(label_vector, format="%Y")
    data_plot.columns = label_vector
    data_plot = data_plot.reset_index()
    if st.session_state.geo_resolution == 'gadm0':
        data_plot = pd.melt(data_plot, id_vars='index', var_name='time', value_name=variable)
    else:
        data_plot = pd.melt(data_plot, id_vars='index', var_name='time', value_name=variable)

    # Plot settings
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

    lines = base.mark_line().encode(size=alt.value(1.5))

    ts_plot = (points + lines).interactive()

    st.altair_chart(ts_plot, use_container_width=True)

# ------------------- #
# Plot choropleth map #
# ------------------- #

with tab2:
    if st.session_state.time_frequency == 'daily':
        st.warning('Choropleth map not available for daily data')
    else:
        world = load_shapes(st.session_state.geo_resolution)
        snapshot_data = world[world.GID_0.isin(row_range)]
        if st.session_state.time_frequency == 'monthly':
            snapshot = st.slider('Snapshot', datetime.datetime(st.session_state.starting_year, 1, 1), datetime.datetime(st.session_state.ending_year, 12, 31), datetime.datetime(st.session_state.starting_year, 1, 1), format="MM/DD/YYYY", help = 'Choose the year to show in the plot')    
            snapshot_data['snapshot'] = data[str(snapshot.strftime("%B%Y"))[0:3].lower() + str(snapshot.strftime("%B%Y"))[-4:]].values
        else:
            snapshot = st.slider('Snapshot', st.session_state.starting_year, st.session_state.ending_year, st.session_state.starting_year, 1, help = 'Choose the year to show in the plot')
            snapshot_data['snapshot'] = data[int(snapshot)].values

        if st.session_state.geo_resolution == 'gadm0':
            snapshot_data.set_index('GID_0', inplace=True)
        else:
            snapshot_data.set_index('NAME_1', inplace=True)

        if options == []:
            st.warning('No country selected')
        else:
            fig = px.choropleth_mapbox(snapshot_data, geojson = snapshot_data.geometry, locations = snapshot_data.index, color = 'snapshot', #color='value', animation_frame="variable",
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
