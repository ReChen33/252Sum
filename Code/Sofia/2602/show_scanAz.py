import os
from typing import Dict
import glob
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter

class showScanAz:

    def __init__(self):

        self.num2Process = 640  # the number of TIME keys to process at a time
        self.path_save = "results/"
        self.sAz_slow_FNs = []
        self.get_slow_FNs_glob = True # whether to get the scan azimuth slow filenames by the function using glob
        self.skip_Ang_Neg = True # whether to skip negative angle values
        self.showAngle_filename = "showAngle.csv"
        self.showTSRC_filename = "showTSRC.csv"


    def slow2Time(self, path = None, scanAz_slow_filename = "20250101_010135_scanAz_slow.txt"):
        """
        From scanAz_slow_2fit_pwv.py

        """
        
        if path is not None:
            #join the path and filename
            scanAz_slow_filename = os.path.join(path, scanAz_slow_filename)

        out_dict: Dict[str, Dict[str,float]] = {}

        #read the scanAz_slow file
        with open(scanAz_slow_filename, 'r') as f:
            with open(self.showAngle_filename, "a+") as angle:
                for line in f:
                    if not (line.startswith('#') or line.startswith('TIME')):  
                        # skip comment lines & col names in scan_Az files
                        parts = line.split()

                        time = parts[0]  # TIME is the first part
                        #need rewrite time to let {time} able to be used as filename
                        time = time.replace('T', ' ')  # format TIME for filename
                        #print("Formatted TIME for filename:", time)
                        
                        EL = float(parts[23])  # elevation is the 24th part
                        AZ = float(parts[24])  # azimuth is the 25th part

                        out_dict[time] = {
                            "TSRC0": float(parts[19]),
                            "TSRC1": float(parts[20]),
                            "TSRC2": float(parts[21]),
                            "TSRC3": float(parts[22]),
                            "EL": EL,
                            "AZ": AZ
                        }
                        if EL < 0 or AZ < 0:
                            if self.skip_Ang_Neg:
                                continue  # skip negative values
                            else:
                                Zen = EL
                        else:
                            Zen = 90 - EL  # calculate zenith angle to elevation

                        time_data = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f') 
                        angle.write(f"{time_data.strftime('%Y-%m-%d %H:%M:%S.%f')},{AZ},{Zen}\n")
            angle.close()
        f.close()

        #print(out_dict)  # print the dictionary to check the data    
        #print(len(out_dict.keys()), "TIME keys found in the dictionary.")
        
        num2Pro = self.num2Process

        for i in range(0, len(out_dict.keys()), num2Pro): 

            if i+(num2Pro) < len(out_dict.keys()):
                # get the current time and its values
                time = list(out_dict.keys())[i:i+num2Pro]  # get the next {num2Pro} TIME keys                
            else:
                time = list(out_dict.keys())[i:]  # get the next {num2Pro} TIME keys

            obs_values: Dict[str, float] = {}
            for t in time:
                for key, value in out_dict[t].items():
                    if key not in obs_values:
                        obs_values[key] = []
                    obs_values[key].append(value)

            #print(obs_values)  # print the obs_values to check the data

            T0 = np.average(obs_values["TSRC0"]) 
            T1 = np.average(obs_values["TSRC1"]) 
            T2 = np.average(obs_values["TSRC2"]) 
            T3 = np.average(obs_values["TSRC3"]) 

            # ---------!!!-----------------------------------------
            # time_range = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f') for t in time]
            # time_range = np.array(time_range)
            # time_pass = time_range[-1] - time_range[0]          
            time_real_mid = datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f') #!!!

            with open(self.showTSRC_filename, "a+") as f:
                f.write(f"{time_real_mid},{T0},{T1},{T2},{T3}\n")
                f.close()

    def getsAzSlowFilenames(self):
        """
        purpose:
            This function returns the list of slow scan azimuth filenames.
        """

        #get global variables
        path_save = self.path_save                 
        sAz_slow_FNs = self.sAz_slow_FNs

        try:
            # get all *_scanAz_slow.txt files in the current directory
            for file in glob.glob(f'{path_save}*_scanAz_slow.txt'):
                file = os.path.basename(file)  # get the filename only
                #print(f"Processing file: {file}")
                sAz_slow_FNs.append(file)
        except Exception as e:
            print(e)

        return sAz_slow_FNs

    def run(self):
        """
        purpose:
            The run func 
        """

        path_save = self.path_save  # path to save the results

        if self.get_slow_FNs_glob:
            # get the slow scan azimuth filenames if {get_slow_FNs_glob} is True
            sAz_slow_FNs = self.getsAzSlowFilenames()
        else:
            sAz_slow_FNs = self.sAz_slow_FNs

        #let sAz_slow_FNs in the order of the time
        sAz_slow_FNs.sort()
        #print(sAz_slow_FNs)

        with open(self.showTSRC_filename, "w+") as TSRC:
            TSRC.write("T_mid,T0_ave,T1_ave,T2_ave,T3_ave\n")

        with open(self.showAngle_filename, "w+") as angle:
            angle.write("Time,AZ,Zen\n")

        for sAz_slow_FN in sAz_slow_FNs:

            self.slow2Time(path = path_save, scanAz_slow_filename = sAz_slow_FN)
            print(f"{sAz_slow_FN} done")


if __name__ == "__main__":
    
    # start_time = perf_counter()

    myShow = showScanAz()
    myShow.num2Process = 1  # number of TIME keys to process at a time
    myShow.skip_Ang_Neg = False  
    SA_FN = "showAngle2602.csv"
    STSRC_FN = "showTSRC2602.csv"
    myShow.showAngle_filename = SA_FN
    myShow.showTSRC_filename = STSRC_FN
    myShow.get_slow_FNs_glob = True
    myShow.path_save = "results260210/"
    #myShow.sAz_slow_FNs = ["20240110_130134_scanAz_slow.txt"]
    myShow.run()
    
    # end_time = perf_counter()

    # print(f"slow write to csv complete take {end_time - start_time}\nread CSV")
    # # make plots
    # start_time = perf_counter()

    # showAngle = pd.read_csv(SA_FN)
    # showTSRC = pd.read_csv(STSRC_FN)

    # try:
    #     showAngle['Time'] = pd.to_datetime(showAngle['Time'], format='%Y-%m-%d %H:%M:%S.%f')
    # except Exception as e:
    #     print(f"Error parsing showAngle['Time']: {e}")

    # try:
    #     showTSRC['T_mid'] = pd.to_datetime(showTSRC['T_mid'], format='%Y-%m-%d %H:%M:%S.%f')
    # except Exception as e:
    #     print(f"Error parsing showTSRC['T_mid']: {e}")
    # end_time = perf_counter()
    # #print(f"csv read complete take {end_time - start_time}")

    # start_time = perf_counter()
    # plt.figure(figsize=(30, 15))

    

    # plt.plot(showAngle['Time'], showAngle['AZ'], label='Azimuth', color='blue', marker='o', linestyle='-')
    # plt.plot(showAngle['Time'], showAngle['Zen'], label='Elevation', color='red', marker='x', linestyle='--')
    # plt.xlabel('Time')
    # plt.ylabel('Angle (degrees)')
    # plt.title('Ang over Time')
    # #plt.yscale('log')
    # plt.grid()
    # plt.legend()
    # plt.xticks(rotation=45)
    
    # plt.savefig('Plots/Ang_over_Time.png',dpi = 1000)
    # # plt.savefig('Plots/Angles_over_Time.svg')

    # plt.hist(showAngle['AZ'], bins=10, color='blue', alpha=0.7)
    # plt.xlabel('Angle (degrees)')
    # plt.ylabel('Number of Occurrences')
    # plt.title('Histogram of Zenith Angles')
    # plt.grid()
    # plt.savefig('Plots/Histogram_Ang.png',dpi = 300)
    # plt.close()

    # plt.hist(showAngle['Zen'], bins=10, color='red', alpha=0.7)
    # plt.xlabel('Angle (degrees)')
    # plt.ylabel('Number of Occurrences')
    # plt.title('Histogram of Zenith Angles')
    # plt.grid()
    # plt.savefig('Plots/Histogram_Zen.png',dpi = 300)
    # plt.close()

    # plt.plot(showTSRC['T_mid'], showTSRC['T0_ave'], label='T0 Average', color='tab:blue', marker='o', linestyle='-')
    # plt.plot(showTSRC['T_mid'], showTSRC['T1_ave'], label='T1 Average', color='tab:orange', marker='x', linestyle='--')
    # plt.plot(showTSRC['T_mid'], showTSRC['T2_ave'], label='T2 Average', color='tab:green', marker='o', linestyle='-')
    # plt.plot(showTSRC['T_mid'], showTSRC['T3_ave'], label='T3 Average', color='tab:purple', marker='x', linestyle='--')
    # plt.xlabel('Time')
    # plt.ylabel('Temperature (K)')
    # plt.title('Temperature over Time')
    # plt.grid()
    # plt.legend()
    # plt.xticks(rotation=45)
    

    # plt.savefig('Plots/Temperature_over_Time.png',dpi = 300)
    # plt.savefig('Plots/Temperature_over_Time.svg')

    # plt.close()

    # plt.hist(showTSRC['T0_ave'], bins=50, color='tab:blue', alpha=0.7, label='T0 Average')
    # plt.hist(showTSRC['T1_ave'], bins=50, color='tab:orange', alpha=0.7, label='T1 Average')
    # plt.hist(showTSRC['T2_ave'], bins=10, color='tab:green', alpha=0.7, label='T2 Average')
    # plt.hist(showTSRC['T3_ave'], bins=10, color='tab:red', alpha=0.7, label='T3 Average')
    # plt.xlabel('Temperature (K)')
    # plt.ylabel('Number of Occurrences')
    # plt.title('Histogram of Temperatures')
    # plt.grid()
    # plt.savefig('Plots/Histogram_Temperature.png',dpi = 300)
    # plt.savefig('Plots/Histogram_Temperature.svg')
    # plt.close()

    # end_time = perf_counter()
    # print(f"Plots done take {end_time - start_time}")

