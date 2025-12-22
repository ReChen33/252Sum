import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pandas as pd
import numpy as np
from metpy.plots import SkewT, Hodograph
import metpy.calc as mpcalc
from metpy.units import units
from datetime import datetime
from siphon.simplewebservice.wyoming import WyomingUpperAir
import os
import glob
import time

base_dir = os.path.dirname(os.path.abspath(__file__))
save_npz_dir = f'{base_dir}/balloon_npz'
if not os.path.exists(save_npz_dir):
    os.makedirs(save_npz_dir)

data_list = []
for month in range(1,13):
    for days in range(1,32):
        try:
            data00 = datetime(2024, month, days, 0)
            data12 = datetime(2024, month, days, 12)
            data_list.append(data00)
            data_list.append(data12)
            if month == 1 or month == 2:
                data00_2025 = datetime(2025, month, days, 0)
                data12_2025 = datetime(2025, month, days, 12)
                data_list.append(data00_2025)
                data_list.append(data12_2025)
        except ValueError:
            print(f'Invalid date {month}/{days}')
            continue
        
data_list.sort()
station = '89009'    

for date in data_list:
    try:
        time.sleep(1)
        df = WyomingUpperAir.request_data(date, station)
        time.sleep(1)
    except Exception as e:
        print(f"Failed to retrieve data for {date} at station {station}: {e}")
        continue

    h = df['height'].values
    p = df['pressure'].values
    T = df['temperature'].values
    Td = df['dewpoint'].values
    u = df['u_wind'].values
    v = df['v_wind'].values
    pwv = df['pw'].values[0]*1000  # convert from mm to um

    #output
    date_64 = np.datetime64(date)
    Per = np.array(p)  
    Tem_C = np.array(T) 
    T_dry = np.array(Td) 
    pwv_value64 = np.float64(pwv) 

    save_fn = f"{save_npz_dir}/Balloon_{date.strftime('%Y%m%d%H%M%S')}.npz"

    if os.path.exists(save_fn):
        print(f"File Balloon_{date.strftime('%Y%m%d%H%M%S')}.npz already exists. Skipping save.")
        continue

    np.savez_compressed(
        save_fn,
            Date=date_64,
            Per=Per,
            Tem_C=Tem_C,
            T_dry=T_dry,
            pwv_am_value=pwv_value64
    )
    print(f"Saved Balloon_{date.strftime('%Y%m%d%H%M%S')}.npz")