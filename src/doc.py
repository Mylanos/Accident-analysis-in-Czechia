#!/usr/bin/env python3.8
# coding=utf-8

from pathlib import Path
import numpy as np
import pandas as pd
import seaborn as sns
import scipy.stats
import matplotlib.pyplot as plt


def load_data(filename: str):
    """This function handles loading of the dataset file and parsing chosen data"""

    # loading of the dataset
    df = pd.read_pickle(filename)

    # two new dataframes for better preservation of rows as there probably wont 
    # be many rows with None's in both cols
    print("Parsing data...")
    data_weather = df[["p37", "p18"]].copy()
    data_visib = df[["p37", "p19"]].copy()

    # replacement of empty strings
    data_weather["p18"] = data_weather["p18"].replace("", np.nan)
    data_weather["p37"] = data_weather["p37"].replace("", np.nan)
    data_visib["p37"] = data_visib["p37"].replace("", np.nan)
    data_visib["p19"] = data_visib["p19"].replace("", np.nan)

    # removal of None values
    data_weather = data_weather.dropna(axis=0, how="any", subset=["p18", "p37"])
    data_visib = data_visib.dropna(axis=0, how="any", subset=["p37", "p19"])

    # datatypes change
    data_weather["p18"] = data_weather["p18"].astype("int16")
    data_weather["p37"] = data_weather["p37"].astype("int16")
    data_visib["p19"] = data_visib["p19"].astype("int16")
    data_visib["p37"] = data_visib["p37"].astype("int16")

    # selecting wanted records(bad records marked as -1, records without any
    # visibility limitations marked as 1,4,6)
    data_weather = data_weather[data_weather["p18"] > 1]  # weather conditions
    data_weather = data_weather[data_weather["p37"] > 0]  # road type
    data_visib = data_visib[data_visib["p37"] > 0]  # road type
    data_visib = data_visib[data_visib["p19"] > 1]  # visibility
    data_visib = data_visib[data_visib["p19"] != 4]
    data_visib = data_visib[data_visib["p19"] != 6]
    return data_weather, data_visib

def process_data(data_weather: pd.DataFrame, data_visib: pd.DataFrame):    
    """ Function processess data, sets labels according to given bins from
        dataset, calculates accidents with given parametres."""

    # parse integer data to given labels
    print("Processing data...")
    typ_silnice = [0, 100, 1000, np.inf]
    names = [
        "dálnice alebo cesta 1. triedy", 
        "cesta 2. triedy", 
        "cesta 3. triedy"
    ]
    data_weather["silnice"] = pd.cut(data_weather["p37"], typ_silnice, labels=names)
    data_visib["silnice"] = pd.cut(data_visib["p37"], typ_silnice, labels=names)

    pocasie_enum = [0, 2, 3, 4, 5, 6, 7]
    pocasie = [
        "jiné stížené",
        "mlha",
        "mrholení",
        "déšť",
        "sněžení",
        "námraza",
        "nárazový vítr",
    ]
    data_weather["Zle pocasie"] = data_weather["p18"].replace(pocasie_enum, pocasie)

    viditelnost_enum = [2, 3, 5, 7]
    viditelnost = [
        "svitání/soumrak",
        "zlé počasie cez den",
        "věrejný osvětlení, noc, zlé počasie",
        "žádné osvětlení, noc, zlé počasie",
    ]
    data_visib["Viditelnost"] = data_visib["p19"].replace(viditelnost_enum, viditelnost)

    # group by data according to studied topic(weather, visibility)
    result1 = (
        data_weather.groupby(["Zle pocasie", "silnice"])["p37"]
        .count()
        .reset_index(name="Počet nehôd")
    )

    result2 = (
        data_visib.groupby(["Viditelnost", "silnice"])["p37"]
        .count()
        .reset_index(name="Počet nehôd")
    )
    return result1, result2

def plot_data(result1: pd.DataFrame, result2: pd.DataFrame):
    """ Function plots statistics of accidents based on visibility and weather
        at the time of the accident."""
    print("Plotting...")
    sns.set(
        rc={
            "axes.grid": True,
            "axes.grid.axis": "y",
            "axes.linewidth": 0.7,
            "axes.facecolor": "linen",
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 7), sharey=True)

    # plots accidents stats by weather conditions
    sns.barplot(
        ax=axes[1],
        data=result1,
        x="silnice",
        y="Počet nehôd",
        hue="Zle pocasie",
        ci="sd",
        palette="YlOrBr",
        alpha=0.9,
    )
    axes[1].set_title("POČET NEHOD PRI ZLOM POČASÍ")
    axes[1].set_xlabel("")

    # plots accidents stats by visibility conditions
    sns.barplot(
        ax=axes[0],
        data=result2,
        x="silnice",
        y="Počet nehôd",
        hue="Viditelnost",
        ci="sd",
        palette="rocket",
        alpha=0.9,
    )
    axes[0].set_title("POČET NEHOD PRI ZHORŠENEJ VIDITELNOSTI A POČASIA")
    axes[0].set_xlabel("")

    fig.tight_layout()
    plt.savefig("fig.png")

def print_data(result1: pd.DataFrame, result2: pd.DataFrame):
    """Prints tables for plots and some interesting hand picked data."""
    print("Printing tables to stdout...")
    print("TABULKA 1:")
    print(result1.to_latex(index=False))
    print("\n\nTABULKA 2:")
    print(result2.to_latex(index=False))
    print("\n\nJednoduchý popis")
    print(f"nehod celkem: {result2['Počet nehôd'].sum()}")
    sumrak = result2[result2["Viditelnost"].str.contains("svitání/soumrak")]
    print(f"nehod pri sumraku/zapadu: {sumrak['Počet nehôd'].sum()}")
    minimum_pocasie = result1["Počet nehôd"].min()
    maximum_pocasie = result1["Počet nehôd"].max()

    najbezpecnejsie = result1[result1["Počet nehôd"] == minimum_pocasie]
    najnebezpecnejsie = result1[result1["Počet nehôd"] == maximum_pocasie]
    print(
        f"najmensi vplyv na nehodovosť z nepriazniveho pocasia malo: {najbezpecnejsie['Zle pocasie'].item()}"
    )
    print(
        f"najvacsi vplyv na nehodovosť z nepriazniveho pocasia malo: {najnebezpecnejsie['Zle pocasie'].item()}"
    )

if __name__ == "__main__":
    main_folder = Path(__file__).parent.parent.resolve()
    print("Loading data...")
    x, y = load_data(main_folder / "accidents.pkl.gz")
    result1, result2 = process_data(x, y)
    plot_data(result1, result2)
    print_data(result1, result2)
