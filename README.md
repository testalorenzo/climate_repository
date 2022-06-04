# The Climate Repository Project

The Climate Repository Project aims at combining climate data from different sources in a single, accessible and organized repository. We offer three ways for accessing data:
- Dashboard access via [Colab](https://colab.research.google.com/drive/15bUqv40_06nZJp3Js4b0muO8vMzJbOO_?usp=sharing)
- Script access via our scripts (retrieval.py in script folder)
- Direct access via GitHub (navigating through this repository)

We let the user choose the preferred source of data. Currently, we offer data from [Climatic Research Unit (CRU TS)](https://www.uea.ac.uk/groups-and-centres/climatic-research-unit), [Delaware Climate Office](https://climate.udel.edu/) and [ECMWF's ERA5](https://www.ecmwf.int/). 

These are the variables, monthly measured, currently supported at both the [GADM](https://gadm.org/) spatial resolution of GADM0 and GADM1 administrative areas:
- Temperature
- Precipitation

Notice that each variable has been weighted by population density in 2010 in such administrative area. Data on population density has been retrieved from [NASA's SEDAC](https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-density-rev11). 

Stay tuned for updates!
