import streamlit as st

st.markdown("# Guide")
st.warning("Page under construction!", icon="⚠️")

"""
* *geo_resolution*: choose among administrative units GADM0 (countries) and GADM1 (bigger administrative units after countries);
* *starting_year* and *ending_year*: window size. Notice that each source provides data for a peculiar time window;
* *time_frequency*: choose among annual or monthly climate data;
* *source*: select source of data (available: CRU TS, UDelaware, HERA5, CSIC);
* *variable*: select variable of interest (available: temperature, precipitation, SPEI);
* *weight*: weight aggregation values by population density;
* *threshold_dummy*: True or False. Number of months over a given threshold for each year in the time window;
* *threshold_kind*: choose among a percentile or an absolute threshold;
* *threshold*: cutoff value.
"""

st.sidebar.markdown('## Contacts')
st.sidebar.markdown('Feel free to send questions, bug reports, documentation issues, and other comments to Marco Gortan (marco.gortan@studbocconi.it) and [Lorenzo Testa](https://testalorenzo.github.io) (l.testa@sssup.it)')
st.sidebar.image("Embeds logo.png", use_column_width=True)
