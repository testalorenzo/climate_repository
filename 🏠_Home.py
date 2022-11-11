import streamlit as st

st.markdown("# Welcome to the Climate Repository Project Dashboard")

"""

The Climate Repository Project provides a user-friendly dashboard to download climate data:
* From different sources in a single, accessible and organized repository
*	Weighted by alternative measures of economic activity at different geographical resolutions

The project is run within the [Institute of Economics](https://www.santannapisa.it/en/istituto/economia) and [EMbeDS](https://www.santannapisa.it/en/department-excellence/embeds) at [Sant'Anna School of Advanced Studies](https://www.santannapisa.it/en) (Pisa, Italy) by [Giorgio Fagiolo](https://sites.google.com/view/giorgiofagiolo/home), Marco Gortan, [Francesco Lamperti](http://www.francescolamperti.eu/) and [Lorenzo Testa](https://testalorenzo.github.io/). 

In the dashboard, the user can choose the preferred **source of climate data**, the **climate variable** of interest – at different geographical and time resolution – and a **weighting scheme**.

## Data sources

## Climate variables

## Weighting scheme

We let the user choose the preferred source of data. Currently, we offer data from [Climatic Research Unit (CRU TS)](https://www.uea.ac.uk/groups-and-centres/climatic-research-unit), [Delaware Climate Office](https://climate.udel.edu/), [ECMWF's ERA5](https://www.ecmwf.int/) and [CSIC](https://spei.csic.es/index.html). 

These are the variables, measured monthly and annually, currently supported at both the [GADM](https://gadm.org/) spatial resolution of GADM0 and GADM1 administrative areas:
* Temperature
* Precipitation
* SPEI (Standardised Precipitation-Evapotranspiration Index) (measured only monthly)

Moreover, we also provide the possibility of weighting climate data by population density or night lights usage (measured in different years) while linking grid data to administrative units. Data on population density have been retrieved from [NASA's SEDAC](https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-density-rev11); data on night lights usage have been retrieved from [Li et al. (2020)](https://www.nature.com/articles/s41597-020-0510-y).

Finally, we also allow the user to specify a percentile or an absolute threshold value of the historic distribution of a geographic unit, counting for each year the number of months that are over the given threshold.

Users that want to run our pipelines on their own data are very welcome to reach us out! 

Stay tuned for updates!
"""

st.sidebar.markdown('## Contacts')
st.sidebar.markdown('Feel free to send questions, bug reports, documentation issues, and other comments to Marco Gortan (marco.gortan@studbocconi.it) and [Lorenzo Testa](https://testalorenzo.github.io) (l.testa@sssup.it)')
st.sidebar.image("Embeds logo.png", use_column_width=True)
