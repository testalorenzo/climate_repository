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
    st.session_state['time_frequency'] = 'monthly'
    st.session_state['starting_year'] = 1951
    st.session_state['ending_year'] = st.session_state.starting_year + 1
    st.session_state['row_range'] = tuple(['USA'])

# ------------ #
# Data imports #
# ------------ #

@st.cache_data(ttl=3600, show_spinner="Fetching country names...")
def load_country_list():
    """
    Load country list from the repository and return a pandas dataframe

    Returns:
    country_list (pandas dataframe): Dataframe containing the country list
    """
    country_list = pd.read_csv('./poly/country_list.csv')
    return country_list

@st.cache_data(ttl=3600, show_spinner="Fetching data...")
def load_data(geo_resolution, variable, source, weight, weight_year, row_range, col_range, time_frequency, threshold_dummy):
    if weight == 'un':
        weight_year = ''

    if time_frequency in ('yearly','monthly'):
        freq = 'monthly'
        time_idx = pd.date_range(start=str(st.session_state.starting_year) + "-01-01",
                                 end= str(st.session_state.ending_year) + "-12-31", freq='MS')
    if time_frequency == 'daily' or threshold_dummy == "True":
        freq = 'daily'
        time_idx = pd.date_range(start=str(st.session_state.starting_year) + "-01-01",
                                 periods=len(row_range), freq='D')

    # TODO: Import regions dictionary mapping GADM0 to GADM1
    if geo_resolution == 'gadm0':
        cols = str(col_range)[1:-1].replace("'", "")
    else:
        regions = pd.read_csv('./poly/gadm1_adm.csv')
        cols = regions.loc[regions.GID_0.isin(col_range), 'GID_1'].tolist()
        cols = str(cols)[1:-1].replace("'", "").replace(".", "_")
    
    file = './data/' + geo_resolution + '_' + source + '_' + variable + '_' + weight + '_' + weight_year + '_' + freq + '.parquet'
    
    query = f"SELECT {cols} FROM '{file}' WHERE Date IN {row_range}"
    imported_data = db.query(query).df()

    imported_data.index = time_idx

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
                 help="Geographical units of observation. gadm0 stands for countries; \
                 gadm1 stands for the first administrative level (states, regions, etc.)", key='geo_resolution')

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
    st.selectbox('Time frequency', ("yearly", "monthly"), index = 0,
                 help = 'Time frequency of the data', key='time_frequency')
elif st.session_state.source == 'ERA5' and st.session_state.weight_year == '2015' and st.session_state.geo_resolution == 'gadm0':
    st.selectbox('Time frequency', ("yearly", "monthly", "daily"), index = 0,
                 help = 'Time frequency of the data', key='time_frequency')
else:
    st.selectbox('Time frequency', ("yearly", "monthly"), index = 0,
                 help = 'Time frequency of the data', key='time_frequency')

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
    st.slider('Starting year', min_year, max_year, key='starting_year')
# Ending year
with col2:
    if st.session_state.time_frequency == 'daily' or st.session_state.threshold_dummy == 'True':
        st.slider('Ending year', st.session_state.starting_year, max_year, key='ending_year')
    else:
        st.slider('Ending year', st.session_state.starting_year, max_year, key='ending_year')

# ------------------- #
# Matching file names #
# ------------------- #

# Rename variables as to match datasets names
if st.session_state.variable == 'temperature':
    variable = 'tmp'
elif st.session_state.variable == 'precipitation':
    variable = 'pre'
else:
    variable = 'spei'
# Introduce string for weights
if st.session_state.weight == 'unweighted':
    weight = 'un'
    st.session_state.weight_year = '2015' # Force weight year to avoid session state error
elif st.session_state.weight == 'night lights':
    weight = 'lights'
else:
    weight = 'pop'


# ------------------- #
# Filter before query #
# ------------------- #

# Extract selected years
if st.session_state.geo_resolution == 'gadm0':
    obs_id = 'GID_0'
else:
    obs_id = 'GID_1'

if st.session_state.time_frequency == 'daily' or st.session_state.threshold_dummy == 'True':
    if st.session_state.ending_year == 2023:
        end_day = '-08-31'
    else:
        end_day = '-12-31'
    time_range = tuple(['X' + str(x).replace('-', '') for x in pd.date_range(start=str(st.session_state.starting_year) + "-01-01",end= str(st.session_state.ending_year) + end_day).format("YYYY.MM.DD") if x != ''])
else:
    time_range = tuple(['X' + str(x) + str(y).rjust(2, '0') for x in range(st.session_state.starting_year, st.session_state.ending_year + 1) for y in range(1,13)])

# Observation filters
world0 = load_country_list()
observation_list = world0.COUNTRY.unique().tolist()
observation_list.sort()
options = st.multiselect('Countries', ['ALL'] + observation_list, default='United States', help = 'Choose the geographical units to show in the plot')

# Build row range
if 'ALL' in options:
    country_range = tuple(world0.GID_0.tolist())
else:
    country_range = tuple(world0.loc[world0.COUNTRY.isin(options), 'GID_0'].tolist())

# --------- #
# Load data #
# --------- #

# Read data from GitHub
data = load_data(st.session_state.geo_resolution, variable, source, weight,
                 st.session_state.weight_year, time_range, country_range,
                 st.session_state.time_frequency, st.session_state.threshold_dummy)

# Summarize if time frequency is yearly
if st.session_state.time_frequency == 'yearly' and st.session_state.threshold_dummy == 'False':
    if variable == 'pre':
        data = data.groupby(np.arange(data.shape[0])//12).sum()
    elif variable == 'tmp':
        data = data.groupby(np.arange(data.shape[0])//12).mean()
    data.index = pd.date_range(start=str(st.session_state.starting_year) + "-01-01",end= str(st.session_state.ending_year) + "-12-31", freq='Y')

elif st.session_state.threshold_dummy == 'True':
    if st.session_state.threshold_kind == 'percentile':
        limit_values = data.quantile(q=st.session_state.threshold/100)
    else:
        limit_values = st.session_state.threshold
    days_over_threshold = data.gt(limit_values, axis=1)
    if st.session_state.time_frequency == 'yearly':
        n_aggregate_over_threshold = days_over_threshold.groupby(by=pd.Grouper(freq="Y")).sum()
    elif st.session_state.time_frequency == 'monthly':
        n_aggregate_over_threshold = days_over_threshold.groupby(by=pd.Grouper(freq="M")).sum()
    data = n_aggregate_over_threshold

# ---------------- #
# Plot time series #
# ---------------- #

tab1, tab2 = st.tabs(['Time series', 'Choropleth map'])

with tab1: 
    data_plot = data
    data_plot = data_plot.reset_index()

    if st.session_state.geo_resolution == 'gadm0':
        data_plot = pd.melt(data_plot, id_vars='index', var_name='country', value_name=variable)
    else:
        data_plot = pd.melt(data_plot, id_vars='index', var_name='country', value_name=variable)

    # Plot settings
    highlight = alt.selection_point(on='mouseover', fields=['index'], nearest=True)

    base = alt.Chart(data_plot).encode(
        x=alt.X('index'),
        y=alt.Y(variable),
        color=alt.Color('country', scale=alt.Scale(scheme='viridis')))

    points = base.mark_circle().encode(
        opacity=alt.value(0),
        tooltip=[
            alt.Tooltip('index', title='index'),
            alt.Tooltip(variable, title=variable),
            alt.Tooltip('country', title='country')
        ]).add_params(highlight)

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
        snapshot_data = world[world.GID_0.isin(country_range)]
        if st.session_state.time_frequency == 'monthly':
            snapshot = st.slider('Snapshot', datetime.datetime(st.session_state.starting_year, 1, 1), 
                                 datetime.datetime(st.session_state.ending_year, 12, 31), 
                                 datetime.datetime(st.session_state.starting_year, 1, 1), 
                                 format="MM-YYYY", help = 'Choose the month to show in the plot')
            snapshot = snapshot.strftime("%Y-%m")
        else:
            snapshot = st.slider('Snapshot', datetime.datetime(st.session_state.starting_year, 1, 1), 
                                 datetime.datetime(st.session_state.ending_year, 12, 31), 
                                 datetime.datetime(st.session_state.starting_year, 12, 31), 
                                 format="YYYY", help = 'Choose the year to show in the plot')
            snapshot = snapshot.strftime("%Y-12-31")

        snapshot_data['snapshot'] = data.loc[pd.Timestamp(snapshot), :].values

        if st.session_state.geo_resolution == 'gadm0':
            snapshot_data.set_index('GID_0', inplace=True)
        else:
            snapshot_data.set_index('NAME_1', inplace=True)

        if options == []:
            st.warning('No country selected')
        else:
            fig = px.choropleth_mapbox(snapshot_data, geojson = snapshot_data.geometry, locations = snapshot_data.index, color = 'snapshot',
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
