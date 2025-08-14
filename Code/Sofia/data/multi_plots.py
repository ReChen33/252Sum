"""
Yifu

purpose: To read text files and plot the 
    4 combinations of data which including TSRC0 TSRC1 TSRC2 TSRC3 EL AZ
    Time? TIME/TIMEWVR
"""


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import glob 

file_list = glob.glob("*.txt")

# for file in file_list:
#     with open(file, 'r') as f:
#         #split the columns by space
#         df = pd.read_csv(f, delim_whitespace=True, skiprows=2)

#         print(df)
#         plt.figure(figsize=(10, 6))
#         #plot line number vs TIMEWVR
#         plt.plot(df.index, df['TIMEWVR'])
#         plt.show()
#     break

# Open the file for reading.
new_f = []


with open('20250102_010135_scanAz_slow.txt', 'r') as f:
    # Read the file line by line
    for line in f:
        if line.startswith('#'):
            continue
        new_f += line.split()

df = pd.DataFrame(new_f)

print(df)
        






