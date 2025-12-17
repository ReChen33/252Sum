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

data_list = []

base_dir = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(base_dir, 'fig1')):
    os.makedirs(os.path.join(base_dir, 'fig1'))

Per_list = []
Tem_list = []
vmr_list = []

amc_list = glob.glob(f'{base_dir}/*.dat.amc') 
amc_list.sort()
#print(amc_list)

data_list = []

for days in range(1,32):
    # data00 = datetime(2024, 1, days, 0)
    data12 = datetime(2024, 1, days, 12) 
    # data_list.append(data00)
    data_list.append(data12)

data_list.sort()
station = '89009'

num_date = 0
num_file_n = 0

while num_date < len(data_list) and num_file_n < len(amc_list):
    
    date = data_list[num_date]
    file_path_n = amc_list[num_file_n]
    file_n = os.path.basename(file_path_n)
    getTime = file_n.split('S')[0]+file_n.split('S')[1].split('.')[0]
    amDate = datetime.strptime(getTime, '%Y%m%d%H%M%S')

    print(f'Processing am {amDate.strftime("%d %H:%M")} with Balloon {date.strftime("%d %H")}')
    try:
        df = WyomingUpperAir.request_data(date, station)        
    except:
        print(f'No data for {station} on {date}')
        num_date += 1
        continue    
    #skip if not the same day
    if date.day < amDate.day:
        print(f'Skipping {date} because it is not on the same day as {amDate}')
        num_date += 1
        continue
    if date.day > amDate.day:
        print(f'Skipping {amDate} because it is not on the same day as {date}')
        num_file_n += 1
        continue
    #compare with balloon data around 12:00 UTC WVR data around 11:50(the one before 12:00 UTC) 
    if abs((date - amDate).total_seconds()) <= 600:            
        print(f'Comparing {date} with {amDate}')
        with open(file_path_n, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if '# P' in line:
                    Per = float(line.split(' ')[2].strip()) #mbar=hPa
                    Per_list.append(Per)
                elif '# T' in line:
                    Tem = float(line.split(' ')[2].strip()) #K
                    Tem_list.append(Tem)    
                elif 'column h2o hydrostatic' in line and '(* ' not in line:
                    vmr = float(line.split(' ')[3].strip()) #g/g
                    vmr_list.append(vmr)
                elif 'column h2o hydrostatic' in line and '(* ' in line:
                    vmr_0 = float(line.split(' ')[3].strip()) #g/g
                    vmr = vmr_0 * float(line.split(')  (* ')[1].strip().split(')')[0])
                    #print(vmr_0, vmr)
                    vmr_list.append(vmr)

        h = df['height'].values
        p = df['pressure'].values
        T = df['temperature'].values
        Td = df['dewpoint'].values
        u = df['u_wind'].values
        v = df['v_wind'].values
        
        WVPP = [v * p for v, p in zip(vmr_list, Per_list)] # Water Vapor Partial Pressure (hPa)
        Tem_C = [t - 273.15 for t in Tem_list] # Temperature (°C)
        SVP = [6.112*np.exp((17.67 * np.array(T)) / (T + 243.5)) for T in Tem_C] # Saturation Vapor Pressure (hPa)

        RH = [WVPP[i] / SVP[i] * 100 for i in range(len(WVPP))]

        b_cons = 17.625
        c_cons = 243.04

        gamma = [np.log(RH[i] / 100) + (b_cons*Tem_C[i]) / (Tem_C[i] + c_cons)  for i in range(len(RH))]
        T_dry = [(c_cons*gamma[i]) / (b_cons - gamma[i]) for i in range(len(gamma))] # Dew Point Temperature (°C)

        T_dry = np.array(T_dry)
        Per = np.array(Per_list)
        Tem_C = np.array(Tem_C)

        fig = plt.figure(figsize=(9, 9))
        skewt2 = SkewT(fig=fig, rotation=45)
        # plot sounding data
        skewt2.plot(Per, Tem_C, 'r', label='am Air Temperature') # air temperature
        skewt2.plot(Per, T_dry, 'b', label='am Dew Point') # dew point
        skewt2.plot(p, T, 'g', ls = '--', label='Balloon  Air Temperature') # air temperature
        skewt2.plot(p, Td, 'y', ls = '--', label='Balloon Dew Point') # dew point

        skewt2.ax.set_xlabel('Temperature (°C)')
        skewt2.ax.set_ylabel('Pressure (hPa)')

        skewt2.ax.legend(loc='best')
        plt.title(f'Skew-T South Pole \n Balloon {date.strftime("%Y-%m-%d %H")} \n am {amDate.strftime("%Y-%m-%d %H:%M:%S")}', 
                fontsize=16)
        fig.savefig(os.path.join(base_dir, f'fig1/SkewT_SP_{amDate.strftime("%Y-%m-%d %H")}.png'), dpi=300)
        #plt.clf()
        plt.close(fig)

        num_date += 1
        num_file_n += 1
    else:
        num_file_n += 1



