import numpy as np
from matplotlib import pyplot as plt
import math
from download import DataDownloader

def plot_stat(data_source, fig_location = None, show_figure = False):

    for row in data_source[1]:
        print(row.values)
        break




N_points = 100000
n_bins = 14

# Generate a normal distribution, center at x=0 and y=5
x = np.random.randn(N_points)
y = .4 * x + np.random.randn(N_points) + 5

fig, axs = plt.subplots(3,1, figsize=(10,13), sharey=True, tight_layout=True)

# We can set the number of bins with the `bins` kwarg
axs[1].hist(x, bins=n_bins)
data_source = DataDownloader().get_list(["VYS"])
plot_stat(data_source)