import numpy as np
from matplotlib import pyplot as plt
import math, re
from download import DataDownloader
from datetime import datetime
from collections import OrderedDict 

def get_accident_stats(data_source):
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

def plot_stat(data_source, fig_location = None, show_figure = False):
    regions = { 
        'PHA': 1, 
        'STC': 2, 
        'JHC': 3,
        'PLK': 4,
        'ULK': 5,
        'HKK': 6,
        'JHM': 7,
        'MSK': 8,
        'OLK': 9,
        'ZLK': 10,
        'VYS': 11,
        'PAK': 12,
        'LBK': 13,
        'KVK': 14 }

    region_stats = get_accident_stats(data_source)
    
    num_of_regions = len(regions.keys())
    x = np.arange(1,num_of_regions + 2, 1)
    x_labels = [region for region in regions.keys()]  + [""]

    #occurance = np.empty([1, 1], dtype=int)
    #region = np.full(region_stats[b], 1)

    a = np.empty([1, 1], dtype=int)
    crash_statistics = {}
    for region in region_stats.keys():
        for year, occurance in sorted(region_stats[region].items()):
            print(region + " = " + str(occurance) + " in " + str(year))
            if year not in crash_statistics.keys():
                crash_statistics[year] = np.full((1, occurance), regions.get(region))
            else:
                new_data = np.full((1, occurance), regions.get(region))
                crash_statistics[year] = np.concatenate([crash_statistics[year], new_data], axis=None)
    print(crash_statistics)
    print(x_labels)
    exit(1)
    fig, axs = plt.subplots(1,1, figsize=(11.69,8.27), sharey=True, tight_layout=True)
    axs.hist(crash_statistics['2020'], bins=x , rwidth=0.6, align='left')
    axs.set_xticks(x)
    axs.set_ylim([0,25000])
    axs.set_xticklabels(x_labels, rotation='horizontal', fontsize=18)
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0, hspace=0)
    plt.show(fig)


data_source = DataDownloader().get_list(None)
plot_stat(data_source)

