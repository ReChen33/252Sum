import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

#read the data from the CSV file
data = pd.read_csv('saveCSV/pwv_backup.csv')
#convert the 'TIME' column to datetime format
date_time = datetime(data['DATE(YYYYMMDD)']) + datetime(data['START TIME(HHMMSS.Microsec)'])
print(date_time)

# #plot the data
# plt.figure(figsize=(10, 5))
# plt.plot(data['TIME'], data['PWV TOTAL zenith'], marker='o', linestyle='-', color='b')
# plt.title('PWV Total Zenith Over Time')
# plt.xlabel('Time')
# plt.ylabel('PWV Total Zenith (mm)')
# plt.xticks(rotation=45)
# plt.grid()
# plt.show()