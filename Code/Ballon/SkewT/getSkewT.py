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

data_list = []

base_dir = os.path.dirname(os.path.abspath(__file__))
save_npz_dir = f'{base_dir}/am_npz'
if not os.path.exists(save_npz_dir):
    os.makedirs(save_npz_dir)

amc_list = glob.glob(f'{base_dir}/*.dat.amc') 
amc_list.sort()
#print(amc_list)

for num_file_n in range(len(amc_list)):
    #print(f'Number of am data: {len(data_list)}')

    file_path_n = amc_list[num_file_n]
    file_n = os.path.basename(file_path_n)
    getTime = file_n.split('S')[0]+file_n.split('S')[1].split('.')[0]
    amDate = datetime.strptime(getTime, '%Y%m%d%H%M%S')

    if amDate.hour not in (22, 23 ,0, 1, 10, 11, 12, 13):  
        continue
    
    Per_list = []
    Tem_list = []
    vmr_list = []
    pwv_am_value = 0

    with open(file_path_n, 'r') as file:
        lines = file.readlines()
        for i in range(len(lines)):
            if '# P' in lines[i]:
                Per = float(lines[i].split(' ')[2].strip()) #mbar=hPa
                #print(Per)
                Per_list.append(Per)
            elif '# T' in lines[i]:
                Tem = float(lines[i].split(' ')[2].strip()) #K
                Tem_list.append(Tem)
            elif 'column h2o hydrostatic' in lines[i] and '(* ' not in lines[i]:
                vmr = float(lines[i].split(' ')[3].strip()) #g/g
                #print(vmr)
                vmr_list.append(vmr)
            elif 'column h2o hydrostatic' in lines[i] and '(* ' in lines[i]:
                vmr_0 = float(lines[i].split(' ')[3].strip()) #g/g
                #print("vmr_0",vmr_0)
                vmr = vmr_0 * float(lines[i].split(')  (* ')[1].strip().split(')')[0])
                #print(vmr_0, vmr)
                vmr_list.append(vmr)
            elif '# total' in lines[i]:
                pwv_am = lines[i+3] #such as (xxx um_pwv)
                pwv_tot_zen = pwv_am.split('(')[1].strip() #remove the (
                pwv_tot_zen = pwv_tot_zen.replace(')', '').strip()  #remove the )
                pwv_tot_zen_value = pwv_tot_zen.replace('um_pwv', '').strip()  #remove the um_pwv
                #print(f'am PWV: {float(pwv_tot_zen_value)} um')
                pwv_am_value = float(pwv_tot_zen_value)
        
    WVPP = [v * p for v, p in zip(vmr_list, Per_list)] # Water Vapor Partial Pressure (hPa)
    Tem_C = [t - 273.15 for t in Tem_list] # Temperature (°C)
    SVP = [6.112*np.exp((17.67 * np.array(T)) / (T + 243.5)) for T in Tem_C] # Saturation Vapor Pressure (hPa)

    RH = [WVPP[i] / SVP[i] * 100 for i in range(len(WVPP))]

    b_cons = 17.625
    c_cons = 243.04

    gamma = [np.log(RH[i] / 100) + (b_cons*Tem_C[i]) / (Tem_C[i] + c_cons)  for i in range(len(RH))]
    T_dry = [(c_cons*gamma[i]) / (b_cons - gamma[i]) for i in range(len(gamma))] # Dew Point Temperature (°C)

    T_dry = np.array(T_dry) #output
    Per = np.array(Per_list) #output
    Tem_C = np.array(Tem_C) #output
    pwv_am_value = pwv_am_value  #output

    #print(type(amDate),type(Per), type(Tem_C), type(T_dry), type(pwv_am_value))
    amDate64 = np.datetime64(amDate)
    pwv_am_value64 = np.float64(pwv_am_value)

    save_am_fn = f"{save_npz_dir}/SkewT_{amDate.strftime('%Y%m%d%H%M%S')}.npz"

    if os.path.exists(save_am_fn):
        print(f"File SkewT_{amDate.strftime('%Y%m%d%H%M%S')}.npz already exists. Skipping save.")
        continue

    np.savez_compressed(
        save_am_fn,
            amDate=amDate64,
            Per=Per,
            Tem_C=Tem_C,
            T_dry=T_dry,
            pwv_am_value=pwv_am_value64
    )

"""
load example:
npz = np.load('SkewT_20230315010000.npz')
print(npz['amDate'])
"""