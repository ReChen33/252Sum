# read scanAZ files plot the line and leap time by plt.hist

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import glob 
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FuncFormatter
import time as t_fun

# 20240612_190135_scanAz_slow for test including bad data
file_list = glob.glob("*_scanAz_slow.txt")
len_list = []
for file in file_list:

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

    #print(len(T_since_Epo))
    len_list.append(len(T_since_Epo))

    # plt.hist(T_since_Epo, bins=100)
    # plt.xlabel('Time since Epoch (seconds)')
    # plt.ylabel('Frequency')
    # plt.title(f'Histogram of Time since Epoch {file}')
    # plt.savefig(f'hist/hist_time_since_epoch_{file}.png')
    # plt.show()

counts, bins, patches = plt.hist(len_list, bins=10, edgecolor='black')
for count, patch in zip(counts, patches):
    # Get the coordinates of the bar
    x = patch.get_x() + patch.get_width() / 2  # Center the text
    y = patch.get_height()                     # Top of the bar

    # Don't label bars with a value of 0
    if count > 0:
        # Add the text with a small offset (y + 2)
        # ha='center' and va='bottom' help with alignment
        plt.text(x, y + 2, int(count), ha='center', va='bottom', fontsize=12)

plt.xlabel('Length of Time since Epoch (seconds)')
plt.ylabel('Number of Occurrences')
plt.title('Histogram of Length of Time since Epoch(with counts)')
plt.savefig(f'hist/hist_length_counts.png')
plt.show()

# plt.ylim(0,(len(file_list)/500))
# plt.title(f'Histogram of Length of Time since Epoch(Y<{(len(file_list)/500)})')
# plt.savefig(f'hist/hist_length_lim_Y_less_{(len(file_list)/500)}.png')

# plt.xlim(1000, 3250)
# plt.title(f'Histogram of Length of Time since Epoch(X:1000-3250)')
# plt.savefig(f'hist/hist_length_lim_X_1000_3250.png')

# plt.ylim(0,len(file_list))
# plt.xlim(3250, 3600)
# plt.title(f'Histogram of Length of Time since Epoch(X:3250-3600)')
# plt.savefig(f'hist/hist_length_lim_X_3250_3600.png')
#plt.show()
plt.close()