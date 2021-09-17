#!/usr/bin/python3.8
# coding=utf-8

import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np
import gzip
import pickle


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:

    """Konvertovani dataframe do geopandas.GeoDataFrame se spravnym kodovani"""
    df = df[df["d"].notna()]
    df = df[df["e"].notna()]
    gdf = geopandas.GeoDataFrame(
        df, geometry=geopandas.points_from_xy(df["d"], df["e"]), 
        crs="EPSG:5514"
    )
    return gdf


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None, 
    show_figure: bool = False
):
    """ Vykresleni grafu s dvemi podgrafy podle lokality nehody """
    if fig_location or show_figure:
        fig, axes = plt.subplots(
            1, 2, figsize=(11.69, 8.27), sharex=True,
            sharey=True
        )
        plk = gdf.query('region == "PLK"')
        plk[plk["p5a"] == 1].plot(
            ax=axes[0],
            markersize=4,
            label="Nehody v obci",
            color="tab:red",
        )
        plk[plk["p5a"] == 2].plot(
            ax=axes[1],
            markersize=4,
            label="Nehody v obci",
            color="tab:green",
        )
        ctx.add_basemap(
            axes[0], crs=plk.crs.to_string(), 
            source=ctx.providers.Stamen.TonerLite
        )
        ctx.add_basemap(
            axes[1], crs=plk.crs.to_string(), 
            source=ctx.providers.Stamen.TonerLite
        )
        axes[0].axis("off")
        axes[0].set_title("Nehody v PLK kraji: v obci", size=15)
        axes[1].axis("off")
        axes[1].set_title("Nehody v PLK kraji: mimo obec", size=15)

        plt.tight_layout()
        if fig_location is not None:
            plt.savefig(fig_location)
        if show_figure:
            plt.show()


def plot_cluster(
    gdf: geopandas.GeoDataFrame, fig_location: str = None, 
    show_figure: bool = False
):
    """Vykresleni grafu s lokalitou nehod v kraji shlukovanych do clusteru"""
    if fig_location or show_figure:
        plk = gdf.query('region == "PLK"')
        # ------------------------
        coords_points = np.dstack([plk.geometry.x, plk.geometry.y]).reshape(-1, 2)
        db = sklearn.cluster.MiniBatchKMeans(n_clusters=17).fit(coords_points)
        db2 = plk.copy()
        db2["cluster"] = db.labels_
        # spojeni dohromad0 (funkce dissolve - geograficky ekvivalent groupby)
        # KOD agregujeme jako pocet (a přejmenujeme na cnt) a plochu sumujeme
        db2 = db2.dissolve(by="cluster", aggfunc={"p1": "count"}).rename(
            columns=dict(p1="cnt")
        )

        coords = geopandas.GeoDataFrame(
            geometry=geopandas.points_from_xy(
                db.cluster_centers_[:, 0], db.cluster_centers_[:, 1]
            )
        )

        db3 = db2.merge(coords, left_on="cluster", right_index=True).set_geometry(
            "geometry_y"
        )

        # Zobrazíme graf tak, že velikost bodu bude odpovídat
        plt.figure(figsize=(11.69, 8.27)) 
        ax = plt.gca()
        ax.axis("off")
        ax.set_title("Nehody v PLK kraji", size=15)
        plk.plot(
            ax=ax,
            markersize=0.2,
            color="tab:grey",
        )
        db3.plot(
            ax=ax, markersize=db3["cnt"], column="cnt", legend=True,
            alpha=0.5
        )
        ctx.add_basemap(
            ax, crs="EPSG:5514", source=ctx.providers.Stamen.TonerLite, 
            alpha=0.6
        )

        plt.tight_layout()
        if fig_location is not None:
            plt.savefig(fig_location)
        if show_figure:
            plt.show()


if __name__ == "__main__":
    # defaultly the output is stored in a file geo1.png/geo2.png files
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", False)
    plot_cluster(gdf, "geo2.png", False)