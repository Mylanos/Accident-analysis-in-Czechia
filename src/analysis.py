#!/usr/bin/env python3.8
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import gzip
import pickle
from pathlib import Path


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    """Vyvorenie dataframu pre sledovane parametre zo subora s datami o nehodovosti v ČR"""
    print("Loading file data...")
    with gzip.open(filename, 'rb') as f:
        content = pickle.load(f)
    if verbose:
        print("orig_size={:.1f} MB".format(content.memory_usage(index=False, deep=True).sum() / 1048576))
    print("Parsing data...")
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
    """Vykreslenie grafu analyzujúceho následky nehôd v jednotlivých regiónoch"""
    # data processing
    print("Processing data...")
    data = df[['p13a', 'p13b', 'p13c', 'region']].copy().groupby(["region"]).sum().reset_index()
    test = df[['p13a', 'region']].copy().groupby(["region"]).count().reset_index()
    data['accidents'] = test['p13a']
    sorted = data.sort_values(by=["accidents"], ascending=False)

    # data visualization
    if fig_location or show_figure:
        print("Plotting consequences graph...")
        sns.set(rc={'axes.grid': True, "axes.grid.axis": "both", "axes.linewidth": 0.7, "axes.facecolor": "lightgrey"})
        fig, axes = plt.subplots(4, 1, sharex=True, figsize=(7.13, 9.4))
        fig.patch.set_facecolor('#e6e6e6')

        sns.barplot(ax=axes[0], x='region', y='p13a', data=sorted, palette='rocket', edgecolor="white")
        axes[0].title.set_text('Počet lidí, kteří zemřeli při nehodě')
        axes[0].set_xlabel('')
        axes[0].set_ylabel('Zemřelo')
        start, end = axes[0].get_ylim()
        axes[0].yaxis.set_ticks(np.arange(start, end, 130))

        sns.barplot(ax=axes[1], x='region', y='p13b', data=sorted, palette='rocket', edgecolor="white")
        axes[1].title.set_text('Počet lidí, kteří byli těžce zranění ')
        axes[1].set_xlabel('')
        axes[1].set_ylabel('Zraněno')
        start, end = axes[1].get_ylim()
        axes[1].yaxis.set_ticks(np.arange(start, end, 500))

        sns.barplot(ax=axes[2], x='region', y='p13c', data=sorted, palette='rocket', edgecolor="white")
        axes[2].title.set_text('Počet lidí, kteří byli lehce zranění')
        axes[2].set_xlabel('')
        axes[2].set_ylabel('Zraněno')
        start, end = axes[2].get_ylim()
        axes[2].yaxis.set_ticks(np.arange(start, end, 3500))

        sns.barplot(ax=axes[3], x='region', y='accidents', data=sorted, palette='rocket', edgecolor="white")
        axes[3].title.set_text('Celkový počet nehod v daném kraji')
        axes[3].set_xlabel('')
        axes[3].set_ylabel('Nehody')
        start, end = axes[3].get_ylim()
        axes[3].yaxis.set_ticks(np.arange(start, end, 30000))

        plt.tight_layout()
        if show_figure:
            plt.show()
        if fig_location:
            print(f"Storing the file... {fig_location}")
            plt.savefig(fig_location)


# Ukol3: příčina nehody a škoda
def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    """Vykreslenie grafu analyzujúceho príčiny nehôd a ich dopad na škody"""
    print("Processing data...")
    bins = [0, 101, 210, 312, 415, 517, 616]
    names = ['nezaviněná řidičem', 'nepřiměřená rychlost jízdy', 'nesprávné předjíždění', 'nedání přednosti v jízdě',
             'nesprávný způsob jízdy', 'technická závada vozidla']
    data = df[['p53', 'p12', 'region']].copy()
    data['p12'] = pd.cut(data['p12'], bins, labels=names)
    ranges = [0, 50, 200, 500, 1000, np.inf]
    ranges_strings = ['<50', '50-200', '200-500', '500-1000', '>1000']
    data['Škoda [tisíc Kč]'] = pd.cut(data['p53'], ranges, labels=ranges_strings)
    result = data.groupby(['region', 'p12', 'Škoda [tisíc Kč]'])['p53'].count().reset_index(name='Počet nehôd')

    # data visualization
    if fig_location or show_figure:
        print("Plotting graph of inflicted damages...")
        sns.set(rc={'axes.grid': True, "axes.grid.axis": "y", "axes.linewidth": 0.7, "axes.facecolor": "lightgrey"})
        fig, axes = plt.subplots(2, 2, figsize=(12, 8.27))
        fig.patch.set_facecolor('#e6e6e6')

        bar1 = sns.barplot(ax=axes[0][0], data=result.query('region == "PHA"'), x="Škoda [tisíc Kč]", y="Počet nehôd", hue="p12", palette="tab10", ci=None , edgecolor="white")
        bar1.set_yscale("symlog")
        bar1.set_title("PHA")
        axes[0][0].get_legend().remove()
        axes[0][0].set_title("PHA")

        bar2 = sns.barplot(ax=axes[0][1], data=result.query('region == "PLK"'), x="Škoda [tisíc Kč]", y="Počet nehôd", hue="p12", palette="tab10", ci=None, edgecolor="white")
        bar2.set_yscale("symlog")
        bar2.set_title("PLK")
        axes[0][1].get_legend().remove()
        axes[0][1].set_title("PLK")

        bar3 = sns.barplot(ax=axes[1][0], data=result.query('region == "JHC"'), x="Škoda [tisíc Kč]", y="Počet nehôd", hue="p12", palette="tab10", ci=None, edgecolor="white")
        bar3.set_yscale("symlog")
        bar3.set_title("JHC")
        axes[1][0].get_legend().remove()
        axes[1][0].set_title("JHC")

        bar4 = sns.barplot(ax=axes[1][1], data=result.query('region == "OLK"'), x="Škoda [tisíc Kč]", y="Počet nehôd", hue="p12", palette="tab10", ci=None, edgecolor="white")
        bar4.set_yscale("symlog")
        bar4.set_title("OLK")
        axes[1][1].set_title("PLK")

        handles, labels = axes[1][1].get_legend_handles_labels()
        plt.legend(handles, labels, title="Příčina nehody", loc='center left', bbox_to_anchor=(1, 0.88), shadow=False, ncol=1)

        plt.tight_layout()
        if show_figure:
            plt.show()
        if fig_location:
            print(f"Storing the file... {fig_location}")
            plt.savefig(fig_location)


# Ukol 4: povrch vozovky
def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """Vykreslenie grafu analyzujúceho stavu vozovky a ich vplyvu na nehodovost"""
    print("Processing data...")
    data = df[['region', 'date', 'p16']].copy()
    crosstable = pd.crosstab(index=[data['region'], data['date']], columns=data['p16'])
    crosstable = crosstable.rename(columns={0: "jiný stav",
                                            1: "suchý neznečistený", 2: "suchý znečistený", 3: "mokrý",
                                            4: "bláto", 5: "náledí(posypané)",
                                            6: "náledí(neposypáno)", 7: "rozlitý olej, nafta apod.",
                                            8: "souvislá sníh",
                                            9: "náhlá změna stavu"})
    grouped = crosstable.groupby(['region', 'date']).sum()
    olk = grouped.query('region == "ZLK"')
    jhc = grouped.query('region == "JHC"')
    jhm = grouped.query('region == "LBK"')
    plk = grouped.query('region == "PLK"')
    olk_result = olk.resample("M", level=1).sum().stack().reset_index().rename(
        columns={0: "Počet nehôd", "date": "Datum vzniku nehody"})
    jhc_result = jhc.resample("M", level=1).sum().stack().reset_index().rename(
        columns={0: "Počet nehôd", "date": "Datum vzniku nehody"})
    jhm_result = jhm.resample("M", level=1).sum().stack().reset_index().rename(
        columns={0: "Počet nehôd", "date": "Datum vzniku nehody"})
    plk_result = plk.resample("M", level=1).sum().stack().reset_index().rename(
        columns={0: "Počet nehôd", "date": "Datum vzniku nehody"})

    # data visualization
    if fig_location or show_figure:
        print("Plotting graph of surface effect on accidents...")
        sns.set(rc={'axes.grid': True, "axes.grid.axis": "both", "axes.linewidth": 0.8, "axes.facecolor": "lightgrey"})
        fig, axes = plt.subplots(2, 2, figsize=(12, 8.27), sharey=True, sharex=True)
        fig.patch.set_facecolor('#e6e6e6')

        sns.lineplot(ax=axes[0][0], x="Datum vzniku nehody", y="Počet nehôd",
                     hue="p16", legend=False,
                     data=olk_result)
        axes[0][0].set_title("OLK")

        sns.lineplot(ax=axes[0][1], x="Datum vzniku nehody", y="Počet nehôd",
                     hue="p16", legend=False,
                     data=jhc_result)
        axes[0][1].set_title("JHC")

        sns.lineplot(ax=axes[1][0], x="Datum vzniku nehody", y="Počet nehôd",
                     hue="p16", legend=False,
                     data=jhm_result)
        axes[1][0].set_title("JHM")

        sns.lineplot(ax=axes[1][1], x="Datum vzniku nehody", y="Počet nehôd",
                     hue="p16",
                     data=plk_result)
        axes[1][1].set_title("PLK")

        handles, labels = axes[1][1].get_legend_handles_labels()
        plt.legend(handles, labels,
                   loc='center left',
                   bbox_to_anchor=(1, 0.78), shadow=False, ncol=1)

        plt.tight_layout()
        if show_figure:
            plt.show()
        if fig_location:
            print(f"Storing the file... {fig_location}")
            plt.savefig(fig_location)


if __name__ == "__main__":
    # defaultly the output is stored in a file 01_nasledky.png/02_priciny.png/03_stav.png
    main_folder = Path(__file__).parent.parent.resolve()
    df = get_dataframe(main_folder / "accidents.pkl.gz")
    plot_conseq(df, fig_location=main_folder / "graphs/01_nasledky.png")
    plot_damage(df, fig_location=main_folder / "graphs/02_priciny.png")
    plot_surface(df, fig_location=main_folder / "graphs/03_stav.png")