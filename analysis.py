#!/usr/bin/env python3.8
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
# import numpy as np
# import os
# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz
import gzip
import pickle


# Ukol 1: nacteni dat
def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    with gzip.open(filename, 'rb') as f:
        content = pickle.load(f)
    if verbose:
        print("orig_size={:.1f} MB".format(content.memory_usage(index=False, deep=True).sum() / 1048576))
    regions = content["region"]
    content = content.iloc[:, 0:-1].astype('category')
    content["date"] = content["p2a"].astype("datetime64[ns]")
    content["p13a"] = content["p13a"].astype("int16")
    content["p13b"] = content["p13b"].astype("int16")

    content["region"] = regions
    content = content.drop(columns=["p2a"])
    if verbose:
        print("new_size={:.1f} MB".format(content.memory_usage(index=False, deep=True).sum() / 1048576))
    return content


# Ukol 2: následky nehod v jednotlivých regionech
def plot_conseq(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    pallete = sns.color_palette("rocket")
    fig, axes = plt.subplots(2, 2)
    fig.suptitle('KEKW')


    accident_deaths = df[['p13a', 'region']].copy()
    result1_grouped = accident_deaths.groupby(["region"]).sum().reset_index().sort_values(by=["p13a"], ascending=False)
    sns.barplot(ax=axes[0, 0], x='region', y='p13a', data=result1_grouped, palette='rocket')

    accident_injuries = df[['p13b', 'region']].copy()
    result2_grouped = accident_injuries.groupby(["region"]).sum().reset_index().sort_values(by=["p13b"], ascending=False)
    sns.barplot(ax=axes[0, 1], x='region', y='p13b', data=result2_grouped, palette='rocket')
    sns.barplot(ax=axes[1, 0], x='region', y='p13b', data=result2_grouped, palette='rocket')
    sns.barplot(ax=axes[1, 1], x='region', y='p13b', data=result2_grouped, palette='rocket')

    plt.show()

# Ukol3: příčina nehody a škoda
def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    pass


# Ukol 4: povrch vozovky
def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    pass


if __name__ == "__main__":
    pass
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    df = get_dataframe("accidents.pkl.gz")
    plot_conseq(df, fig_location="01_nasledky.png", show_figure=True)
    # plot_damage(df, "02_priciny.png", True)
    # plot_surface(df, "03_stav.png", True)
