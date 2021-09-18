# Analysis-of-accident-statistics-in-CZ
Processing and visualising statistics from publicly available data of accidents in Czech Republic. 
Sets of scripts that downloads data from endpoint provided by our university, containing official data statistics of accidents in Czech Republic. 
Data gets processed into dataframes, then gets analysed in certain factors/properties and the result of the analysis is visualised.

## Project Structure
```
├── accidents.pkl.gz
├── data
│   ├── datagis-09-2020.zip
│   ├── datagis-rok-2017.zip
│   ├── datagis-rok-2018.zip
│   ├── datagis-rok-2019.zip
│   └── datagis2016.zip
├── doc.pdf
├── graphs
│   ├── 01_nasledky.png
│   ├── 02_priciny.png
│   ├── 03_stav.png
│   ├── fig.png
│   ├── geo1.png
│   └── geo2.png
├── notebooks
│   ├── 03-bonus.ipynb
│   ├── data.sqlite
│   ├── devel.sqlite
│   └── stat.ipynb
├── requirements.txt
├── src
│   ├── analysis.py
│   ├── doc.py
│   ├── download.py
│   ├── geo.py
│   └── get_stat.py
├── zadanie_cast1.pdf
└── zadanie_cast2.pdf
```

- **accidents.pkl.gz** - data file downloaded from publicly available sites. [(url)](https://www.policie.cz/clanek/statistika-nehodovosti-900835.aspx?q=Y2hudW09NQ%3d%3d)
- **Data** - processed data stored by certain years
- **doc.pdf** - simple infographics
- **graphs**
    - **01_nasledky.png** - graphics containing analysis of consequences of different types of accidents (analysis.py)
    - **02_priciny.png**  - graphics containing analysis of damage done by certain type of accident (analysis.py)
    - **03_stav.png** - graphics analysing impact of certain surfaces on accidents(analysis.py)
    - **fig.png** - graphics analysing impact of certain weather on accidents(analysis.py)
    - **geo1.png** - geographical graphics visualising accidents on a map(analysis.py)
    - **geo2.png** - geographical graphics visualising clusters of accidents on a map(analysis.py)
- **notebooks**
    - **03-bonus.ipynb** - bonus task scraping alza list of products and storing them in a local SQLite3 DB
    - **data.sqlite** - data DB
    - **devel.sqlite** - data DB
    - **stat.ipynb** - statistics calculations, testing of a certain hypothesis.
- **requirements.txt** - required packages
- **src**
    - **analysis.py** - analysis and visualising
    - **doc.py** - generates simples infographic in LateX
    - **download.py** - downloader of the accidents data
    - **geo.py** - geographical graphics visualising
    - **get_stat.py** - simple statistics
─ **zadanie_cast1.pdf** - assignment
─ **zadanie_cast2.pdf** - assignment

## Graphics output example
Exact accidents locations  |  Cluster accidents location
:-------------------------:|:-------------------------:
![geo1.png](https://github.com/Mylanos/Accident-analysis-in-Czechia/blob/8259e738b9d958a6dd038c67dc4f236478b4cc25/graphs/geo1.png) | ![geo2.png](https://github.com/Mylanos/Accident-analysis-in-Czechia/blob/8259e738b9d958a6dd038c67dc4f236478b4cc25/graphs/geo2.png)

