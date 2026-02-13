
import pandas as pd
import matplotlib.pyplot as plt
from time import perf_counter

# make plots
#start_time = perf_counter()

showAngle = pd.read_csv('showAngle2602.csv')
showTSRC = pd.read_csv('showTSRC2602.csv')

try:
    showAngle['Time'] = pd.to_datetime(showAngle['Time'], format='%Y-%m-%d %H:%M:%S.%f')
except Exception as e:
    print(f"Error parsing showAngle['Time']: {e}")

try:
    showTSRC['T_mid'] = pd.to_datetime(showTSRC['T_mid'], format='%Y-%m-%d %H:%M:%S.%f')
except Exception as e:
    print(f"Error parsing showTSRC['T_mid']: {e}")
# end_time = perf_counter()
# print(f"csv read complete take {end_time - start_time}")

# start_time = perf_counter()

plt.figure(figsize=(30, 15))
plt.scatter(showAngle['Time'], showAngle['AZ'], label='Azimuth', color='blue', linestyle='-')
plt.xlabel('Time', fontsize=20)
plt.ylabel('Angle (degrees)', fontsize=20)
plt.title('AZ over Time', fontsize=24)
plt.grid()
plt.legend()
plt.xticks(rotation=20)
# plt.xlim(showAngle['Time'][0], showAngle['Time'][3500])
plt.savefig('Plots/AZ_over_Time2602.png',dpi = 300)
plt.show()
plt.close()



