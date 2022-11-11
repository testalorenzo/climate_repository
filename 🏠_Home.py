import streamlit as st

st.markdown("# Welcome to the Climate Repository Project Dashboard")

"""

The Climate Repository Project provides a user-friendly dashboard to download climate data:
* From different sources in a single, accessible and organized repository
*	Weighted by alternative measures of economic activity at different geographical resolutions

The project is run within the [Institute of Economics](https://www.santannapisa.it/en/istituto/economia) and [EMbeDS](https://www.santannapisa.it/en/department-excellence/embeds) at [Sant'Anna School of Advanced Studies](https://www.santannapisa.it/en) (Pisa, Italy) by [Giorgio Fagiolo](https://sites.google.com/view/giorgiofagiolo/home), Marco Gortan, [Francesco Lamperti](http://www.francescolamperti.eu/) and [Lorenzo Testa](https://testalorenzo.github.io/). 

In the dashboard, the user can choose the **climate variable** of interest – at different geographical and time resolution and from different data sources – and a **weighting scheme**.

## Climate variables
The dashboard allows the user to choose: 
* *Data source*: we currently support data from [Climatic Research Unit (CRU TS)](https://www.uea.ac.uk/groups-and-centres/climatic-research-unit), [Delaware Climate Office](https://climate.udel.edu/), [ECMWF's ERA5](https://www.ecmwf.int/) and [CSIC](https://spei.csic.es/index.html)
* *Climate variable*: available climate variables are temperature and precipitation (monthly and annual observations) and SPEI (standardized precipitation-evapotranspiration index; monthly observations)
* *Geographical resolution*: data can be downloaded at both the [GADM](https://gadm.org/) spatial resolution of GADM0 (World countries) and GADM1 administrative areas (i.e. regions within World countries)
* *Time range*: depending on the data source of climate variables, the user can set starting and ending years of time range of interest

## Weighting scheme
We provide the possibility of weighting climate data by measures of economic activity while linking grid data to administrative units. The dashboard allows the user to choose:
*	*Weighting type*: there are currently three options: (i) no weights (i.e., download raw climate data); or weighting climate data by gridded (ii) population density from [NASA's SEDAC](https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-density-rev11); (iii) night lights usage (from [Li et al. 2020](https://www.nature.com/articles/s41597-020-0510-y))
*	*Weighting year*: depending on the weighting type, the user can choose the base year, i.e. the year of observation of the weighting variable


Finally, we also allow the user to specify a percentile or an absolute threshold value of the historic distribution of a geographic unit, counting for each year the number of months that are over the given threshold.

Users that want to run our pipelines on their own data are very welcome to reach us out! 

Stay tuned for updates!
"""

st.sidebar.markdown('## Contacts')
st.sidebar.markdown('Feel free to send questions, bug reports, documentation issues, and other comments to Marco Gortan (marco.gortan@studbocconi.it) and [Lorenzo Testa](https://testalorenzo.github.io) (l.testa@sssup.it)')
st.sidebar.image("Embeds logo.png", use_column_width=True)
