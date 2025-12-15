import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pandas as pd

from metpy.plots import SkewT, Hodograph
import metpy.calc as mpcalc
from metpy.units import units

from datetime import datetime

from siphon.simplewebservice.wyoming import WyomingUpperAir

import os

data_list = []

base_dir = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(base_dir, 'fig')):
    os.makedirs(os.path.join(base_dir, 'fig'))

#create error log txt file
with open(os.path.join(base_dir, 'error_log.txt'), 'w+') as f:
    f.write('Error Log\n')
    f.write('========= ========= =========\n\n')

years = [2024,2025]
for month in range(1,13):
    for days in range(1,31):
        try:
            data00_2024 = datetime(years[0], month, days, 0)
            data12_2024 = datetime(years[0], month, days, 12)

            data_list.append(data00_2024)
            data_list.append(data12_2024)

            if month == 1 or month == 2:
                data00_2025 = datetime(years[1], month, days, 0)
                data12_2025 = datetime(years[1], month, days, 12)
                data_list.append(data00_2025)
                data_list.append(data12_2025)

        except:
            with open(os.path.join(base_dir, 'error_log.txt'), 'a') as f:
                f.write(f'Invalid date: {years[0]}-{month}-{days}\n')
            continue

with open(os.path.join(base_dir, 'error_log.txt'), 'a') as f:
    f.write(f'Total valid dates to process: {len(data_list)}\n\n')


station = '89009'

for date in data_list:
    try:
        df = WyomingUpperAir.request_data(date, station)
    except:
        print(f'No data for {date.strftime("%Y-%m-%d %H:%M UTC")}')
        with open(os.path.join(base_dir, 'error_log.txt'), 'a') as f:
            f.write(f'No data for {date.strftime("%Y-%m-%d %H:%M UTC")}\n')
        continue

    #print(df.head())

    h = df['height'].values
    p = df['pressure'].values
    T = df['temperature'].values
    Td = df['dewpoint'].values
    u = df['u_wind'].values
    v = df['v_wind'].values

    # make figure and `SkewT` object
    fig = plt.figure(figsize=(9, 9))
    skewt = SkewT(fig=fig, rotation=45)

    # plot sounding data
    skewt.plot(p, T, 'r', label='Air Temperature')  # air temperature
    skewt.plot(p, Td, 'b', label='Dew Point')  # dew point
    skewt.plot_barbs(p[p >= 100], u[p >= 100], v[p >= 100])  # wind barbs
    skewt.ax.legend(loc='best')

    plt.title(f'Skew-T \n South Pole {date.strftime("%Y-%m-%d %H:%M UTC")}', fontsize=16)
    fig.savefig(os.path.join(base_dir, f'fig/SkewT_SP_{date.strftime("%Y_%m_%d_%H")}.png'), dpi=300)
    #plt.clf()
    plt.close(fig)
    

