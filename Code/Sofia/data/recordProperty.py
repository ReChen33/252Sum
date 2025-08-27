"""
Ver 0.0
Before class
Ver 0.1
Add timer 


"""

import numpy as np
import pandas as pd

import glob 
import time as t_fun


# 20240612_190135_scanAz_slow for test including bad data
file_list = glob.glob("*_scanAz_slow.txt")
file_list.sort()

len_list = []
#print(file_list)
save_arr = np.array([])
save_arr = save_arr.reshape(0, 21)
time_take = np.array([])

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
    T_since_Epo = np.zeros(len(time))
    for i in range(1, len(time)+1):
        #time[i] = time[i].replace('T', ' ')
        #print(time[i])
        T_since_Epo[i-1] = t_fun.mktime(t_fun.strptime(time[i], "%Y-%m-%dT%H:%M:%S.%f"))

###
    if len(T_since_Epo) < 3420:
        continue

    num2Pro = 315

    for i in range(0, len(T_since_Epo), num2Pro):  
        #save npy files
        Time_start = T_since_Epo[i]

        if i + num2Pro - 1 < len(T_since_Epo):
            end = i+num2Pro-1
            chunk_end = i+num2Pro
        else:
            end = -1
            chunk_end = -1

        Time_end = T_since_Epo[end]

        Time_avg = T_since_Epo[i + (chunk_end - i)//2]
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

        save_arr = np.append(save_arr, [[Time_start, Time_end, Time_avg, Time_leap, data_point, T0_max, T0_min, T0_avg, T0_std, T1_max, T1_min, T1_avg, T1_std, T2_max, T2_min, T2_avg, T2_std, T3_max, T3_min, T3_avg, T3_std]], axis=0)

    time_take_end_one = t_fun.perf_counter()
    print(f"Time taken for {file}: {time_take_end_one - time_take_start_one} seconds")
    time_take = np.append(time_take, time_take_end_one - time_take_start_one)

np.save(f"ProTest.npy", save_arr)

time_take_end_overall = t_fun.perf_counter()
print(f"Overall time taken: {time_take_end_overall - time_take_start_overall} seconds")
time_take = np.append(time_take, time_take_end_overall - time_take_start_overall)
np.save(f"ProTest_time.npy", time_take)