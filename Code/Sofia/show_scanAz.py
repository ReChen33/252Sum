import os
from typing import Dict
import glob
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

class showScanAz:

    def __init__(self):
        """
        Initialize the slow2FitPWV class.

        variable:
            self.num2Process: int, the number of TIME keys to process at a time
            self.path_save: str, the path to save the results
            self.sAz_slow_FNs: list, the list of slow scan azimuth filenames
            self.get_sAz_slow_FNs: bool, whether to get the slow scan azimuth filenames by glob
            self.am_temp: str, the am fit template file
            self.time_take_file: str, the file to save the time taken for each TIME
            self.date_pwv_file: str, the file to save the date and PWV values
        """

        self.num2Process = 640  # the number of TIME keys to process at a time
        self.path_save = "results/"
        self.sAz_slow_FNs = []
        self.get_slow_FNs_glob = True # whether to get the scan azimuth slow filenames by the function using glob
        self.am_temp = "SPole_annual_50.amc"
        self.time_take_file = 'time_take.csv'  # file to save the time taken for each TIME
        self.date_pwv_file = 'time_pwv.csv'  # file to save the date and PWV values
        self.percentage = 0.3  # percentage to find the extreme peak, default is 30%

    def slow2Time(self, path = None, scanAz_slow_filename = "20250101_010135_scanAz_slow.txt"):
        """
        From scanAz_slow_2fit_pwv.py

        """
        
        if path is not None:
            #join the path and filename
            scanAz_slow_filename = os.path.join(path, scanAz_slow_filename)


        #use a Dict to save the data
        """out_dict = 
            ["TIME":
                ["TSRC0":[value list], "TSRC1":[value list], "TSRC2":[value list], 
                "TSRC3":[value list], "EL":[value list], "AZ":[value list]]
            ]
        """
        out_dict: Dict[str, Dict[str,float]] = {}

        #read the scanAz_slow file
        with open(scanAz_slow_filename, 'r') as f:
            for line in f:
                if not (line.startswith('#') or line.startswith('TIME')):  
                    # skip comment lines & col names in scan_Az files
                    parts = line.split()

                    time = parts[0]  # TIME is the first part
                    #need rewrite time to let {time} able to be used as filename
                    time = time.replace(':', '').replace('-', '').replace(' ', '_').replace('T', ' ')  # format TIME for filename
                    #print("Formatted TIME for filename:", time)

                    out_dict[time] = {
                        "TSRC0": float(parts[19]),
                        "TSRC1": float(parts[20]),
                        "TSRC2": float(parts[21]),
                        "TSRC3": float(parts[22]),
                        "EL": float(parts[23]),
                        "AZ": float(parts[24])
                    }
        f.close()
        #print(out_dict)  # print the dictionary to check the data    
        print(len(out_dict.keys()), "TIME keys found in the dictionary.")

        # num4Time = 0 #to see how many done by py

        #A for loop to create the dat files based on diff TIME

        num2Pro = self.num2Process



        for i in range(0, len(out_dict.keys()), num2Pro):  # process {num2Pro} entries at a time
            #print(i+num2Pro, "out of", len(out_dict.keys()), "TIME keys processed.")

            if i+(num2Pro) < len(out_dict.keys()):
                # get the current time and its values
                time = list(out_dict.keys())[i:i+num2Pro]  # get the next {num2Pro} TIME keys
                #time_name = f"{time[0]}E{time[num2Pro-1][-13:]}"
                
            else:
                time = list(out_dict.keys())[i:]  # get the next {num2Pro} TIME keys
                #time_name = f"{time[0]}E{time[-1][-13:]}"

            
            #time_name = time_name.replace(' ', 'S')
            
            #print(f"For {time_name}\n\t{time_data} {time_s} {time_e}")
            #Example: "20250101S010136.531267E010146.233995"
            #print(f"Processing TIME: {time_name}")

            obs_values: Dict[str, float] = {}
            for t in time:
                for key, value in out_dict[t].items():
                    if key not in obs_values:
                        obs_values[key] = []
                    obs_values[key].append(value)

            #print(obs_values)  # print the obs_values to check the data

            T0 = np.average(obs_values["TSRC0"]) #***
            T1 = np.average(obs_values["TSRC1"]) #***
            T2 = np.average(obs_values["TSRC2"]) #***
            T3 = np.average(obs_values["TSRC3"]) #***
            EL = np.array(obs_values["EL"]) #***
            AZ = np.array(obs_values["AZ"]) #***

            Zen = 90 - EL  # calculate zenith angle to elevation

            time_10min = [datetime.strptime(t, '%Y%m%d %H%M%S.%f') for t in time]
            #print(f"Time range: {time_10min[0]} to {time_10min[-1]}")

            time_pass = time_10min[-1] - time_10min[0]            
            time_real_mid = time_10min[0] + time_pass #***
            #print(time_real_mid)
            plt.subplot(2,1,1)
            plt.scatter(time_real_mid, T0, label=f'TSRC0',color='black')
            plt.scatter(time_real_mid, T1, label=f'TSRC1',color='red')
            plt.scatter(time_real_mid, T2, label=f'TSRC2',color='green')
            plt.scatter(time_real_mid, T3, label=f'TSRC3',color='blue')

            plt.subplot(2,1,2)
            plt.plot(time_10min, Zen, label=f'Zenith', color='red')
            plt.plot(time_10min, AZ, label=f'Azimuth', color='green')

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

        num4sAzFN = 0
        plt.figure(figsize=(20, 12))  # create a figure for plotting
        for sAz_slow_FN in sAz_slow_FNs:
            num4sAzFN += 1  # count the number of slow scan azimuth files processed

            self.slow2Time(path = path_save, scanAz_slow_filename = sAz_slow_FN)

            #show number of time sAz_slow_FN processed
            #print(f"Processed: {sAz_slow_FN} \n{num4sAzFN} in {len(sAz_slow_FNs)} slow scan azimuth files.")
        plt.subplot(2,1,1)
        plt.title('Scan Azimuth Data')
        plt.xlabel('Time') 
        plt.ylabel('Temperature (K)')
        plt.grid()
        plt.legend()

        plt.subplot(2,1,2)
        plt.title('Scan Azimuth Data')
        plt.xlabel('Time') 
        plt.ylabel('Azimuth Angle (degrees)')
        plt.grid()
        plt.legend()
        
        plt.savefig(f"testShow.png", dpi=300)

        plt.show()


if __name__ == "__main__":
    myShow = showScanAz()
    myShow.num2Process = 312  # number of TIME keys to process at a time
    myShow.get_slow_FNs_glob = False
    myShow.sAz_slow_FNs = ["20250101_010135_scanAz_slow.txt"]
    myShow.run()
