#!/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np
# muzeze pridat vlastni knihovny
import gzip
import pickle


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """ Konvertovani dataframe do geopandas.GeoDataFrame se spravnym kodovani"""
    gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df["d"], df["e"]),
                                 crs="EPSG:5514")
    return gdf


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s dvemi podgrafy podle lokality nehody """
    if fig_location or show_figure:
        fig, axes = plt.subplots(1, 2, figsize=(17, 8))
        jhm = gdf.query('region == "JHM"')
        jhm[jhm["p5a"] == 1].plot(ax=axes[0], markersize=4, label="Nehody v obci", color="tab:red",)
        jhm[jhm["p5a"] == 2].plot(ax=axes[1], markersize=4, label="Nehody v obci", color="tab:green",)
        ctx.add_basemap(axes[0], crs=jhm.crs.to_string(), source=ctx.providers.Stamen.TonerLite)
        ctx.add_basemap(axes[1], crs=jhm.crs.to_string(), source=ctx.providers.Stamen.TonerLite)
        axes[0].axis('off')
        axes[0].set_title('Nehody v JHM kraji: v obci', size=15)
        axes[1].axis('off')
        axes[1].set_title('Nehody v JHM kraji: mimo obec', size=15)

        plt.tight_layout()
        if show_figure:
            plt.show()
        if fig_location:
            plt.savefig(fig_location)


def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """
    jhm = gdf.query('region == "JHM"')
    jhm_points = jhm[jhm["p5a"] == 1]
    print(jhm_points)
    print(jhm_points.centroid)

if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    # plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)


"""
fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    path = geopandas.datasets.get_path('naturalearth_lowres')

    world = geopandas.read_file(path)
    gdp_max = world['gdp_md_est'].max()
    gdp_min = world['gdp_md_est'].min()

    world.plot(ax=ax, facecolor='lightgrey', edgecolor='grey', )

    max_size = 40
    min_size = 1

    # world.centroid.plot(ax=ax, color='red')
    for (idx, country), cd in zip(world.iterrows(), world.centroid):
        gdp = country['gdp_md_est']
        plt.plot(cd.xy[0], cd.xy[1],
                 marker='o',
                 color='red',
                 markersize=min_size + (max_size - min_size) * (gdp / gdp_max),
                 transform=ccrs.Geodetic(),
                 alpha=0.75,
                 )

    # end for
    plt.show()
"""
