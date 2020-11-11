import numpy as np
from matplotlib import pyplot as plt
import math
import re
from download import DataDownloader
from datetime import datetime
import argparse as ap
import os
import errno


def get_accident_stats(data_source):
    """parses the np.ndarray and coverts it to dictionary of statistics"""
    content = data_source[1]
    current_date = str(np.datetime64(content[0]['f5']).astype('datetime64[Y]'))
    current_region = str(content[0]['f66'])
    region_stats = {current_date: 0}
    stats = {}
    for i in range(len(content)):
        date = str(np.datetime64(content[i]['f5']).astype('datetime64[Y]'))
        region = str(content[i]['f66'])
        if(current_region != region):
            stats[current_region] = region_stats
            region_stats = {current_date: 0}
            current_region = region
        if(current_date == date):
            region_stats[date] += 1
        else:
            region_stats[date] = 1
            current_date = date
    stats[current_region] = region_stats
    return stats


def yearly_stats_by_regions(region_stats):
    """processes occurances of a crash by a year in given regions"""
    stats = {}
    for region in region_stats.keys():
        for year, occurance in sorted(region_stats[region].items()):
            if year not in stats.keys():
                stats[year] = [occurance]
            else:
                stats[year].append(occurance)
    return stats


def label_bars(rects, ax, indexes):
    """labels bars in graph with order of accident occurances"""
    for i, rect in enumerate(rects):
        if(indexes[i] == 0):
            rect.set_color('#38aef2')
        else:
            rect.set_color('#1085c9')
        height = rect.get_height()
        ax.annotate('{}'.format(indexes[i]+1),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 1),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


def plot_stat(data_source, fig_location=None, show_figure=False):
    """labels bars in graph with order of accident occurances"""
    regions = {'PHA': 1, 'STC': 2, 'JHC': 3, 'PLK': 4, 'ULK': 5, 'HKK': 6, 'JHM': 7, 'MSK': 8,
               'OLK': 9, 'ZLK': 10, 'VYS': 11, 'PAK': 12, 'LBK': 13, 'KVK': 14}

    region_stats = get_accident_stats(data_source)
    x = np.arange(len(regions.keys()))
    x_labels = [region for region in regions.keys()]
    year_statistics = yearly_stats_by_regions(region_stats)

    num_of_years = len(year_statistics.keys())
    width = 0.5
    fig, axs = plt.subplots(
        num_of_years, 1, figsize=(8.27, 12), tight_layout=True)
    fig.patch.set_facecolor('#898c8a')

    for i, year in enumerate(year_statistics.keys()):
        sorted_stats = year_statistics[year].copy()
        h = np.array(sorted_stats, dtype=int)
        sorted_indexes = np.argsort(np.argsort(-h, kind='mergesort'))
        rects = axs[i].bar(x, year_statistics[year], width)
        label_bars(rects, axs[i], sorted_indexes)
        axs[i].yaxis.grid(color='black', linestyle="--", linewidth=0.7)
        axs[i].set_axisbelow(True)
        axs[i].set_ylabel("Počet nehôd")
        axs[i].set_title(year)
        axs[i].set_xticks(x)
        axs[i].set_xticklabels(x_labels, rotation='horizontal', fontsize=12)

    plt.suptitle(
        "Počet nehôd na území Českej Republiky v jednotlivých rokoch", fontsize=14)
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95,
                        top=0.95, wspace=0, hspace=0)
    if(show_figure is not None):
        plt.show()
    if(fig_location is not None):
        plt.savefig(fig_location + '/plot.png')
    plt.show()

def dir_path(path):
    if not os.path.isdir(path):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise   
            pass
    return path


if __name__ == "__main__":
    parser = ap.ArgumentParser(description="get_stat.py")
    parser.add_argument("--fig_location", type=dir_path)
    parser.add_argument("--show_figure")
    arguments, leftovers = parser.parse_known_args()
    data_source = DataDownloader().get_list(None)
    plot_stat(data_source, arguments.fig_location, arguments.show_figure)
