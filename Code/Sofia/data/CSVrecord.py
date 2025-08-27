"""
like recordProperty.py
but use CSV output
"""

import numpy as np
import pandas as pd

import glob 
import time as t_fun
from datetime import datetime

# 20240612_190135_scanAz_slow for test including bad data
file_list = glob.glob("*_scanAz_slow.txt")
file_list.sort()

len_list = []
#print(file_list)

time_FN = "ProTest_time.csv"
FN = "ProTest.csv"

with open(time_FN, 'w+') as t:
    t.write("Event Name,Time Taken (s)\n")
with open(FN, 'w+') as t:
    t.write("Time Start,Time End,Time Avg,Time Leap,Data Point,T0 Max,T0 Min,T0 Avg,T0 Std,T1 Max,T1 Min,T1 Avg,T1 Std,T2 Max,T2 Min,T2 Avg,T2 Std,T3 Max,T3 Min,T3 Avg,T3 Std\n")


time_take_start_overall = t_fun.perf_counter()

for file in file_list:

    time_take_start_one = t_fun.perf_counter()

    new_f = []

    with open(file, 'r') as f:
        # Read the file line by line
        for line in f:
            if line.startswith('#'):
                continue
            split_rows = line.split()
            new_f.append(split_rows)

    df = pd.DataFrame(new_f)


    time = df[0][1:] #format: 2024-06-12T19:12:05.551599
    timewvr = df[1][1:].astype(float)
    T0 = df[19][1:].astype(float)
    T1 = df[20][1:].astype(float)
    T2 = df[21][1:].astype(float)
    T3 = df[22][1:].astype(float)
    El = df[23][1:].astype(float)
    AZ = df[24][1:].astype(float)

    #convert {time} in local time to seconds since the Epoch
    T_since_Epo = list(range(len(time)))
    for i in range(1, len(time)+1):
        #time[i] = time[i].replace('T', ' ')
        #print(time[i])
        time[i] = time[i].replace('T', ' ')
        T_since_Epo[i-1] = datetime.strptime(time[i], "%Y-%m-%d %H:%M:%S.%f")

###
    if len(T_since_Epo) < 3420:
        continue

    num2Pro = 314

    for i in range(0, len(T_since_Epo), num2Pro):  
        #save npy files
        Time_start = T_since_Epo[i]

        if i + num2Pro - 1 < len(T_since_Epo):
            chunk_end = i+num2Pro
        else:
            chunk_end = -1

        Time_end = T_since_Epo[chunk_end-1]
        Time_avg = T_since_Epo[i + (chunk_end - i)//2].strftime("%Y-%m-%d %H:%M:%S.%f")
        Time_leap = Time_end - Time_start

        T0_chunk = T0[i:chunk_end]
        T0_max = np.max(T0_chunk)
        T0_min = np.min(T0_chunk)
        T0_avg = np.mean(T0_chunk)
        T0_std = np.std(T0_chunk)

        T1_chunk = T1[i:chunk_end]
        T1_max = np.max(T1_chunk)
        T1_min = np.min(T1_chunk)
        T1_avg = np.mean(T1_chunk)
        T1_std = np.std(T1_chunk)

        T2_chunk = T2[i:chunk_end]
        T2_max = np.max(T2_chunk)
        T2_min = np.min(T2_chunk)
        T2_avg = np.mean(T2_chunk)
        T2_std = np.std(T2_chunk)

        T3_chunk = T3[i:chunk_end]
        T3_max = np.max(T3_chunk)
        T3_min = np.min(T3_chunk)
        T3_avg = np.mean(T3_chunk)
        T3_std = np.std(T3_chunk)

        data_point = len(T0_chunk)

        with open(FN, 'a+') as t:
            t.write(f"{Time_start},{Time_end},{Time_avg},{Time_leap},{data_point},{T0_max},{T0_min},{T0_avg},{T0_std},{T1_max},{T1_min},{T1_avg},{T1_std},{T2_max},{T2_min},{T2_avg},{T2_std},{T3_max},{T3_min},{T3_avg},{T3_std}\n")

    time_take_end_one = t_fun.perf_counter()
    print(f"Time taken for {file}: {time_take_end_one - time_take_start_one} seconds")
    time_event_name = file
    time_taken = time_take_end_one - time_take_start_one
    with open(time_FN, 'a+') as t:
        t.write(f"read {time_event_name},{time_taken:.4f}\n")

time_take_end_overall = t_fun.perf_counter()
print(f"Overall time taken: {time_take_end_overall - time_take_start_overall} seconds")
with open(time_FN, 'a+') as t:
    t.write(f"Overall,{time_take_end_overall - time_take_start_overall:.4f}\n")
