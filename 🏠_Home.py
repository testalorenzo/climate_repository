import streamlit as st

st.markdown("# Welcome to the Climate Repository Project Dashboard")

"""

The Climate Repository Project aims at combining climate data from different sources in a single, accessible and organized repository. We offer three ways for accessing data:
* Dashboard access via our web app
* Script access via our scripts
* Direct access via GitHub

We let the user choose the preferred source of data. Currently, we offer data from [Climatic Research Unit (CRU TS)](https://www.uea.ac.uk/groups-and-centres/climatic-research-unit), [Delaware Climate Office](https://climate.udel.edu/), [ECMWF's ERA5](https://www.ecmwf.int/) and [CSIC](https://spei.csic.es/index.html). 

These are the variables, measured monthly and annually, currently supported at both the [GADM](https://gadm.org/) spatial resolution of GADM0 and GADM1 administrative areas:
* Temperature
* Precipitation
* SPEI (Standardised Precipitation-Evapotranspiration Index) (measured only monthly)

Moreover, we also provide the possibility of weighting climate data by population density or night lights usage in 2015 while linking grid data to administrative units. Data on population density have been retrieved from [NASA's SEDAC](https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-density-rev11); data on night lights usage have been retrieved from [Henderson et al. (2012)](https://www.aeaweb.org/articles?id=10.1257/aer.102.2.994).

Finally, we also allow the user to specify a percentile or an absolute threshold value of the historic distribution of a geographic unit, counting for each year the number of months that are over the given threshold.

Users that want to run our pipelines on their own data can freely access our scripts on GitHub. 

Stay tuned for updates!
"""

st.sidebar.markdown('## Contact')
st.sidebar.markdown('Feel free to send questions, bug reports, documentation issues, and other comments to Marco Gortan (m.gortan@studbocconi.it) and [Lorenzo Testa](https://testalorenzo.github.io) (l.testa@sssup.it)')
st.sidebar.image("Embeds logo.png", use_column_width=True)
