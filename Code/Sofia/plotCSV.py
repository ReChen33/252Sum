
import pandas as pd
import matplotlib.pyplot as plt
from time import perf_counter

# make plots
start_time = perf_counter()

showAngle = pd.read_csv('showAngle.csv')
showTSRC = pd.read_csv('showTSRC.csv')

try:
    showAngle['Time'] = pd.to_datetime(showAngle['Time'], format='%Y-%m-%d %H:%M:%S.%f')
except Exception as e:
    print(f"Error parsing showAngle['Time']: {e}")

try:
    showTSRC['T_mid'] = pd.to_datetime(showTSRC['T_mid'], format='%Y-%m-%d %H:%M:%S.%f')
except Exception as e:
    print(f"Error parsing showTSRC['T_mid']: {e}")
end_time = perf_counter()
print(f"csv read complete take {end_time - start_time}")

start_time = perf_counter()
plt.figure(figsize=(30, 15))



plt.plot(showAngle['Time'], showAngle['AZ'], label='Azimuth', color='blue', marker='o', linestyle='-')
plt.plot(showAngle['Time'], showAngle['Zen'], label='Elevation', color='red', marker='x', linestyle='--')
plt.xlabel('Time')
plt.ylabel('Angle (degrees)')
plt.title('Ang over Time')
#plt.yscale('log')
plt.grid()
plt.legend()
plt.xticks(rotation=45)

plt.savefig('Plots/Ang_over_Time.png',dpi = 300)
# plt.savefig('Plots/Angles_over_Time.svg')
plt.close()

plt.hist(showAngle['AZ'], bins=10, color='blue', alpha=0.7)
plt.xlabel('Angle (degrees)')
plt.ylabel('Number of Occurrences')
plt.title('Histogram of AZ')
plt.grid()
plt.savefig('Plots/Histogram_AZ.png',dpi = 300)
plt.close()

plt.hist(showAngle['Zen'], bins=1, color='red', alpha=0.7)
plt.xlabel('Angle (degrees)')
plt.ylabel('Number of Occurrences')
plt.title('Histogram of Zenith Angles')
plt.grid()
plt.savefig('Plots/Histogram_Zen.png',dpi = 300)
plt.close()

plt.plot(showTSRC['T_mid'], showTSRC['T0_ave'], label='T0 Average', color='tab:blue', marker='o', linestyle='-')
plt.plot(showTSRC['T_mid'], showTSRC['T1_ave'], label='T1 Average', color='tab:orange', marker='x', linestyle='--')
plt.plot(showTSRC['T_mid'], showTSRC['T2_ave'], label='T2 Average', color='tab:green', marker='o', linestyle='-')
plt.plot(showTSRC['T_mid'], showTSRC['T3_ave'], label='T3 Average', color='tab:purple', marker='x', linestyle='--')
plt.xlabel('Time')
plt.ylabel('Temperature (K)')
plt.title('Temperature over Time')
plt.grid()
plt.legend()
plt.xticks(rotation=45)


plt.savefig('Plots/Temperature_over_Time.png',dpi = 300)
plt.savefig('Plots/Temperature_over_Time.svg')

plt.close()

plt.hist(showTSRC['T0_ave'], bins=10, color='tab:blue', alpha=0.7, label='T0 Average')
plt.hist(showTSRC['T1_ave'], bins=10, color='tab:orange', alpha=0.7, label='T1 Average')
plt.hist(showTSRC['T2_ave'], bins=10, color='tab:green', alpha=0.7, label='T2 Average')
plt.hist(showTSRC['T3_ave'], bins=10, color='tab:red', alpha=0.7, label='T3 Average')
plt.xlabel('Temperature (K)')
plt.ylabel('Number of Occurrences')
plt.title('Histogram of Temperatures')
plt.grid()
plt.savefig('Plots/Histogram_Temperature.png',dpi = 300)
plt.savefig('Plots/Histogram_Temperature.svg')
plt.close()

end_time = perf_counter()
print(f"Plots done take {end_time - start_time}")

