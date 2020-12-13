#!/usr/bin/env python3.8
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
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
    content["p13c"] = content["p13c"].astype("int16")
    content["p12"] = content["p12"].astype("int32")
    content["p53"] = content["p53"].astype("int32")
    content["p53"] = content["p53"].div(10)

    content["region"] = regions
    content = content.drop(columns=["p2a"])
    if verbose:
        print("new_size={:.1f} MB".format(content.memory_usage(index=False, deep=True).sum() / 1048576))
    return content


# Ukol 2: následky nehod v jednotlivých regionech
def plot_conseq(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    pallete = sns.color_palette("rocket")
    fig, axes = plt.subplots(4, 1, sharex=True, figsize=(6.13, 5.4))
    fig.patch.set_facecolor('#e6e6e6')

    data = df[['p13a', 'p13b', 'p13c', 'region']].copy().groupby(["region"]).sum().reset_index()
    test = df[['p13a', 'region']].copy().groupby(["region"]).count().reset_index()
    data['accidents'] = test['p13a']
    sorted = data.sort_values(by=["accidents"], ascending=False)

    sns.barplot(ax=axes[0], x='region', y='p13a', data=sorted, palette='rocket')
    axes[0].title.set_text('Počet lidí, kteří zemřeli při nehodě')
    axes[0].set_xlabel('')
    axes[0].set_ylabel('Zemřelo')
    axes[0].yaxis.grid(color='black', linestyle="--", linewidth=0.7)
    axes[0].set_axisbelow(True)
    start, end = axes[0].get_ylim()
    axes[0].yaxis.set_ticks(np.arange(start, end, 130))

    sns.barplot(ax=axes[1], x='region', y='p13b', data=sorted, palette='rocket')
    axes[1].title.set_text('Počet lidí, kteří byli těžce zranění ')
    axes[1].set_xlabel('')
    axes[1].set_ylabel('Zraněno')
    axes[1].yaxis.grid(color='black', linestyle="--", linewidth=0.7)
    axes[1].set_axisbelow(True)
    start, end = axes[1].get_ylim()
    axes[1].yaxis.set_ticks(np.arange(start, end, 500))

    sns.barplot(ax=axes[2], x='region', y='p13c', data=sorted, palette='rocket')
    axes[2].title.set_text('Počet lidí, kteří byli lehce zranění')
    axes[2].set_xlabel('')
    axes[2].set_ylabel('Zraněno')
    axes[2].yaxis.grid(color='black', linestyle="--", linewidth=0.7)
    axes[2].set_axisbelow(True)
    start, end = axes[2].get_ylim()
    axes[2].yaxis.set_ticks(np.arange(start, end, 4000))

    sns.barplot(ax=axes[3], x='region', y='accidents', data=sorted, palette='rocket')
    axes[3].title.set_text('Celkový počet nehod v daném kraji')
    axes[3].set_xlabel('')
    axes[3].set_ylabel('Nehody')
    axes[3].yaxis.grid(color='black', linestyle="--", linewidth=0.7)
    axes[3].set_axisbelow(True)
    start, end = axes[3].get_ylim()
    axes[3].yaxis.set_ticks(np.arange(start, end, 30000))

    plt.tight_layout()
    plt.show()


# Ukol3: příčina nehody a škoda
def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.27))

    selected_regions = ['PHA', 'PLK', 'JHC', 'OLK']
    bins = [0, 101, 210, 312, 415, 517, 616]
    names = ['nezaviněná řidičem', 'nepřiměřená rychlost jízdy', 'nesprávné předjíždění', 'nedání přednosti v jízdě',
             'nesprávný způsob jízdy', 'technická závada vozidla']
    data = df[['p53', 'p12', 'region']].copy()
    data['p12'] = pd.cut(data['p12'], bins, labels=names)
    ranges = [0, 50, 200, 500, 1000, np.inf]
    ranges_strings = ['<50', '50-200', '200-500', '500-1000', '>1000']
    data['range'] = pd.cut(data['p53'], ranges, labels=ranges_strings)
    result = data.groupby(['region', 'p12', 'range'])['p53'].count().reset_index(name='count')

    bar1 = sns.barplot(ax=axes[0][0],
        data=result.query('region == "PHA"'), x="range", y="count", hue="p12", palette="tab10", ci=None
                        , edgecolor="white")
    bar1.set_yscale("symlog")
    bar1.set_title("PHA")
    axes[0][0].set(xlabel='Škoda [tisíc Kč]', ylabel='Počet')
    axes[0][0].get_legend().remove()

    bar2 = sns.barplot(ax=axes[0][1],
                      data=result.query('region == "PLK"'), x="range", y="count", hue="p12", palette="tab10", ci=None
                      , edgecolor="white")
    bar2.set_yscale("symlog")
    bar2.set_title("PLK")
    axes[0][1].set(xlabel='Škoda [tisíc Kč]', ylabel='')
    axes[0][1].get_legend().remove()

    bar3 = sns.barplot(ax=axes[1][0],
                      data=result.query('region == "JHC"'), x="range", y="count", hue="p12", palette="tab10", ci=None
                      , edgecolor="white")
    bar3.set_yscale("symlog")
    bar3.set_title("JHC")
    axes[1][0].set(xlabel='Škoda [tisíc Kč]', ylabel='Počet')
    axes[1][0].get_legend().remove()

    bar4 = sns.barplot(ax=axes[1][1],
                      data=result.query('region == "OLK"'), x="range", y="count", hue="p12", palette="tab10", ci=None
                      , edgecolor="white")
    bar4.set_yscale("symlog")
    bar4.set_title("OLK")
    axes[1][1].set(xlabel='Škoda [tisíc Kč]', ylabel='')

    #fig.subplots_adjust(bottom=0.3, wspace=0.33)
    handles, labels = axes[1][1].get_legend_handles_labels()
    plt.legend(handles, labels,
               loc='center left',
               bbox_to_anchor=(1, 0.88), shadow=False, ncol=1)
    plt.tight_layout()
    plt.show()


# Ukol 4: povrch vozovky
def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.27))

    data = df[['region', 'date', 'p16']].copy()
    crosstable = pd.crosstab(index=[data['region'], data['date']], columns=data['p16'])
    crosstable = crosstable.rename(columns={0: "jiný stav",
                                     1: "suchž neznečistený", 2: "suchý znečistený", 3: "mokrý",
                                     4: "bláto", 5: "náledí(posypané)",
                                     6: "náledí(neposypáno)", 7: "rozlitý olej, nafta apod.",
                                     8: "souvislá sníh",
                                     9: "náhlá změna stavu"})
    grouped = crosstable.groupby(['region', 'date']).sum()
    olk = grouped.query('region == "OLK"')
    pha = grouped.query('region == "PHA"')
    jhm = grouped.query('region == "JHM"')
    plk = grouped.query('region == "PLK"')
    olk_result = olk.resample("M", level=1).sum().stack().reset_index().rename(columns={0: "count"})
    pha_result = pha.resample("M", level=1).sum().stack().reset_index().rename(columns={0: "count"})
    jhm_result = jhm.resample("M", level=1).sum().stack().reset_index().rename(columns={0: "count"})
    plk_result = plk.resample("M", level=1).sum().stack().reset_index().rename(columns={0: "count"})

    sns.lineplot(ax=axes[0][0], x="date", y="count",
                 hue="p16", legend=False,
                 data=olk_result)

    sns.lineplot(ax=axes[0][1], x="date", y="count",
                hue="p16", legend=False,
                data=pha_result)

    sns.lineplot(ax=axes[1][0], x="date", y="count",
                hue="p16", legend=False,
                data=jhm_result)

    sns.lineplot(ax=axes[1][1], x="date", y="count",
                hue="p16",
                data=plk_result)

    handles, labels = axes[1][1].get_legend_handles_labels()
    plt.legend(handles, labels,
               loc='center left',
               bbox_to_anchor=(1, 0.68), shadow=False, ncol=1)
    plt.tight_layout()

    plt.show()
    pass


if __name__ == "__main__":
    pass
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    df = get_dataframe("accidents.pkl.gz")
    # plot_conseq(df, fig_location="01_nasledky.png", show_figure=True)
    # plot_damage(df, "02_priciny.png", True)
    plot_surface(df, "03_stav.png", True)
