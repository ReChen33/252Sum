"""
25/07/17

Ver 4.5
    add more comments

Yifu

Purpose:
This code should show the PWV for diff time measurement for file 20250101_010135_scanAz_slow.txt
Use the am fit by SPole_annual_50.amc(included the fit columns)

"""

import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict
from time import perf_counter
from datetime import datetime
import glob
from time import sleep
import statistics as stats

class slow2FitPWV:
    """
    A class to handle the slow scan Azimuth data and the fit PWV values using am fits.  

    How this class works:
        1. Initialize the class
        2. run method
            2.1 clean the old csv files bc we going to create new ones
            2.2 if get_slow_FNs_glob is True, get the slow scan azimuth filenames by glob package
            2.3 for each filename call the slow2Dat method
        3. slow2Dat method
            3.1 if {path_save} not None join the path to inputs FNs
            3.2 use {out_dict} to save the data read from the file
            3.3 call timeTake method to save the time taken to read the file
            3.4 for each TIME key in {out_dict}, create a dat file
                3.4.1 call peakOut method to find the extreme peak in the values
            3.5 call dat2Am method to create am files based on the dat file
            3.6 call remove_old_files method to remove old am files to save space
            3.7 The if-break of num4Time only for testing
        4. dat2Am method
            4.1 call am command to create am files based on the dat file (os.system)
            4.2 rewrite the {time} to remove the folders' name
            4.3 call read_am method to write to time_pwv.csv file based on the amc file
        5. read_am methods
            5.1 read the *.dat.amc files and write to time_pwv.csv file
        
    Necessary methods:
        step 1: slow2Dat: read the *_scanAz_slow.txt file and write a dat file
        step 2: dat2Am: use the am fits to create amc;ams;amr files based on the dat file
        step 3: read_am: read the *.dat.amc files and write to time_pwv.csv file

    Math methods:
        timeTake: save the time taken for each event into the time_take.csv file
        sum_time_take: sum the time taken for each time_event in the time_take.csv file
        peakOut: find the extreme peak(more than 50%) in a list of numbers, and remove it to give a new average number.

    Not necessary methods:
        remove_old_files: remove am files for saving space
        
    """ 

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


    def remove_old_files(self,path_save = "results/"):
        """"
        purpose:
        remove old .dat, .dat.amc, .dat.ams, and .dat.amr files in the specified path to save space
        """
        
        try:
            for file in glob.glob(f'{path_save}*.dat'):
                #print(f"Not Removing File: {file}")
                os.remove(file)
            for file in glob.glob(f'{path_save}*.dat.amc'):
                #print(f"Not Removing File: {file}")
                os.remove(file)
            for file in glob.glob(f'{path_save}*.dat.ams'):
                #print(f"Not Removing File: {file}")
                os.remove(file)
            for file in glob.glob(f'{path_save}*.dat.amr'):
                #print(f"Not Removing File: {file}")
                os.remove(file)

        except Exception as e:
            print(f"Error removing files: {e}")

        #print("am fit files removed done.")

    def read_am(self, all_lines_variable:list, time:str, zen_ang:float):
        """
        purpose:
            Read the *.dat.amc files 

            write to time_pwv.csv file
                DATE(YYYYMMDD)
                START TIME(HHMMSS.Microsec)
                END TIME(HHMMSS.Microsec)
                TIME PASSED (sec)
                PWV TOTAL zenith
                PWV TOTAL line-of-sight
                zenith angle
                standard_deviation_of_residuals
                Nscale_troposphere_h2o

            based on lines information in the *.dat.amc file, not on the index #

        input:
            all_lines_variable: list[str], the lines of the *.dat.amc file

        """

        std_line = ""
        nscale_line = ""
        pwv_line_total = ""

        for i in range(len(all_lines_variable)):
            #print("reading line:", i, all_lines_variable[i].strip())

            if all_lines_variable[i].startswith('# standard deviation of residuals'):
                std_line = all_lines_variable[i]

            if all_lines_variable[i].startswith('Nscale troposphere h2o'):
                nscale_line = all_lines_variable[i]

            if all_lines_variable[i].startswith('# total'):
                pwv_line_total = all_lines_variable[i+3]
                #print(f"pwv_line_total: {pwv_line_total}")


        #nscale_line=all_lines_variable[45] # get the nscale line(Ln 46)
        nscale_com = nscale_line.split(' ')[0]  #get the nscale comment
        nscale_com += "_" + nscale_line.split(' ')[1]
        nscale_com += "_" + nscale_line.split(' ')[2]
        #print('nscale_com=', nscale_com)

        nscale_value = nscale_line.split(' ')[3].strip()  #get the nscale value
        #print('nscale_value=', nscale_value)

        #std_line=all_lines_variable[10] 
        std_com = std_line.split(' ')[1]  #get the std comment
        std_com += "_" + std_line.split(' ')[2]
        std_com += "_" + std_line.split(' ')[3]
        std_com += "_" + std_line.split(' ')[4]
        
        std_value = std_line.split(' ')[5].strip()  
        std_unit = std_line.split(' ')[6].strip()  
        #print('std_line=', std_line)

        # pwv_line_meso=all_lines_variable[484]
        # pwv_line_strato=all_lines_variable[491]
        # pwv_line_tropo=all_lines_variable[498]

        #for SPole_annual_50.amc, index is 505
        #pwv_line_total=all_lines_variable[505]

        #for ACT_annual_50_fit.amc, index is 463(Ln 464)
        #pwv_line_total=all_lines_variable[463] 

        # print('pwv_line_meso=', pwv_line_meso)
        # print('pwv_line_strato=', pwv_line_strato)
        # print('pwv_line_tropo=', pwv_line_tropo)
        # print('pwv_line_total=', pwv_line_total)

        #{time} except: "20250101S010136.531267E010146.233995"
        time_date = time.split('S')[0]  # get the date part (YYYYMMDD)   
        time_start = time.split('S')[1]  # get the start time part
        time_start = time_start.split('E')[0]  # remove the end time part
        time_end = time.split('E')[1]  # get the end time part

        time_start_cal = datetime.strptime(time_date+time_start, "%Y%m%d%H%M%S.%f")
        time_end_cal = datetime.strptime(time_date+time_end, "%Y%m%d%H%M%S.%f")

        time_pass = (time_end_cal - time_start_cal).total_seconds()  # get the time passed part

        pwv_tot_zen = pwv_line_total.split('(')[1].strip() #remove the (
        pwv_tot_zen = pwv_tot_zen.replace(')', '').strip()  #remove the )

        pwv_tot_LoS = pwv_line_total.split('(')[2].strip() #remove the (
        pwv_tot_LoS = pwv_tot_LoS.replace(')', '').strip()  #remove the )

        date_pwv_file = self.date_pwv_file

        #save the time and pwv values to a file
        if not os.path.exists(date_pwv_file):
            with open(date_pwv_file, 'w') as pwv_file:
                pwv_file.write(f"DATE(YYYYMMDD),START TIME(HHMMSS.Microsec),END TIME(HHMMSS.Microsec),TIME PASSED (sec),PWV TOTAL zenith,PWV TOTAL line-of-sight,zenith angle,{std_com},{nscale_com}\n")
                pwv_file.write(f"{time_date},{time_start},{time_end},{time_pass},{pwv_tot_zen},{pwv_tot_LoS},{zen_ang},{std_value} {std_unit},{nscale_value}\n")
            pwv_file.close()
        else:
            with open(date_pwv_file, 'a') as pwv_file:
                pwv_file.write(f"{time_date},{time_start},{time_end},{time_pass},{pwv_tot_zen},{pwv_tot_LoS},{zen_ang},{std_value} {std_unit},{nscale_value}\n")
            pwv_file.close()

    def dat2Am(self, am_temp_inp = "SPole_annual_50.amc", zen_ang = 45, dat_fn_inp = "test.dat", path = None):
        """
        purpose:
        use the am fits(am manual Ch7) to create amc;ams;amr files 
        based on the {am_template}, {zen_ang}, and {dat_filename}   

        input:
            am_template: str, the am template filename
            zen_ang: float, the zenith angle
            dat_filename: str, the dat filename

        output:
            None, 
            but creates {dat_filename}.amc; {dat_filename}.ams; {dat_filename}.amr files
        """

        os.system(f"am {am_temp_inp} {zen_ang} {dat_fn_inp}")
        #print(f"{dat_fn_inp} created using {am_temp_inp} at zenith angle {zen_ang} degrees.")

        sleep(0.001) #wait in case the system is slow

        #read the PWV from the new amc
        file_variable = open(dat_fn_inp+'.amc')
        all_lines_variable = file_variable.readlines()
        file_variable.close()

        #get the time from the dat_fn_inp
        time = dat_fn_inp
        if path is not None:
            # {time} except: "~/results/20250101S010147.191706E010156.795119_scanAz_slow.dat"
            time = time.split('/')[-1] 
        time = time.split('_')[0]  

        # read the amc file and write to time_pwv.csv    
        self.read_am(all_lines_variable, time, zen_ang)  


    def peakOut(self, numbers, percentage=0.5):
        
        """
        Purpose: 
            Find the extreme peak(more than 50%) in a list of numbers, and remove it to give a new average number.

        input:
            A list of numbers.

        output:
            A new average value of the list without the extreme peak.

        """

        med = stats.median(numbers)
        #print("median: ", med)
        
        threshold_low = med * (1 - percentage)
        #print("threshold_low: ", threshold_low)
        threshold_high = med * (1 + percentage)
        #print("threshold_high: ", threshold_high)
        new_numbers = []

        for number in numbers:
            if number <= threshold_low or number >= threshold_high:
                continue
            else:
                new_numbers.append(number)

        aver = np.average(new_numbers)
        return aver

    def timeTake(self, time_event_name, time_taken:float):
        """
        purpose:
            save the time taken for each event into the time_take.csv file

        input:
            time_event_name: str, the name of the time event
            time_taken: float, the time taken for the event

        output:
            None
        But creates or appends to the time_take.csv file
        """

        time_take_FN = self.time_take_file

        if not os.path.exists(time_take_FN):
            with open(time_take_FN, 'w') as t:
                t.write("TIME,take TIME (seconds)\n")
                t.write(f"{time_event_name},{time_taken:.4f}\n")
            t.close()
        else:
            with open(time_take_FN, 'a') as t:
                t.write(f"{time_event_name},{time_taken:.4f}\n")
            t.close()

    def slow2Dat(self, path = None, scanAz_slow_filename = "20250101_010135_scanAz_slow.txt", am_temp = "SPole_annual_50.amc"):
        """
        purpose:
            read the *_scanAz_slow.txt file and write a dat file

        file format:
            from *_scanAz_slow.txt we need: TIME(0); TSRC0(19); TSRC1(20); TSRC2(21); TSRC3(22); EL(23); AZ(24)
            into dat:(for each col. which means diff channel) fre; bandwith; Temp

        input:
            scanAz_slow_filename: str, the filename of the scanAz_slow file, 
                                default is "20250101_010135_scanAz_slow.txt"
            am_temp: str, the am fit template file, default is "SPole_annual_50.amc"


        """
        read_time_start = perf_counter()  # start the timer for reading the file

        if path is not None:
            #join the path and filename
            scanAz_slow_filename = os.path.join(path, scanAz_slow_filename)

        am_temp_4dat = am_temp #used in loop to function dat2Am

        if path is not None:
            am_temp_4dat = os.path.join(path, am_temp_4dat)

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
                    time = time.replace(':', '').replace('-', '').replace(' ', '_')  # format TIME for filename
                    
                    out_dict[time] = {
                        "TSRC0": float(parts[19]),
                        "TSRC1": float(parts[20]),
                        "TSRC2": float(parts[21]),
                        "TSRC3": float(parts[22]),
                        "EL": float(parts[23]),
                        "AZ": float(parts[24])
                    }
        f.close()

        read_time_end = perf_counter()  # end the timer for reading the file

        time_taken = read_time_end - read_time_start  # calculate the time taken to read the file
        
        # save the time taken to the file
        self.timeTake(f"read {scanAz_slow_filename}", time_taken)  

        #print(out_dict)  # print the dictionary to check the data    
        print(len(out_dict.keys()), "TIME keys found in the dictionary.")
        
        num4Time = 0 #to see how many done by py

        #A for loop to create the dat files based on diff TIME

        num2Pro = self.num2Process

        for i in range(0, len(out_dict.keys()), num2Pro):  # process {num2Pro} entries at a time
            #print(i+num2Pro, "out of", len(out_dict.keys()), "TIME keys processed.")
            
            if i+(num2Pro) < len(out_dict.keys()):
                # get the current time and its values
                time = list(out_dict.keys())[i:i+num2Pro]  # get the next {num2Pro} TIME keys
                #print(f"time list: {time}")

                time_name = f"{time[0]}E{time[num2Pro-1][-13:]}"
            else:
                time = list(out_dict.keys())[i:]  # get the next {num2Pro} TIME keys
                time_name = f"{time[0]}E{time[-1][-13:]}"
            #Example: "20250101S010136.531267E010146.233995"
            time_name = time_name.replace('T', 'S')
            
            #print(f"Processing TIME: {time_name}")

            obs_values: Dict[str, float] = {}
            for t in time:
                for key, value in out_dict[t].items():
                    if key not in obs_values:
                        obs_values[key] = []
                    obs_values[key].append(value)

            #print(obs_values)  # print the obs_values to check the data

            
            start = perf_counter()  # start the timer

            #write the dat filename based on the time
            dat_filename = f"{time_name}_scanAz_slow.dat"

            if path is not None:
                dat_filename = os.path.join(path, dat_filename)

            
            T0, T1, T2, T3, EL = 0.0, 0.0, 0.0, 0.0, 0.0
            #AZ = 0.0  # AZ is not used right now

            for i in range(len(obs_values["TSRC0"])):
                T0 += obs_values["TSRC0"][i]
                T1 += obs_values["TSRC1"][i]
                T2 += obs_values["TSRC2"][i]
                T3 += obs_values["TSRC3"][i]
                EL += obs_values["EL"][i]
                #AZ += obs_values["AZ"][i]
            
            #average the values by peakOut function
            T0 = self.peakOut(obs_values["TSRC0"])
            T1 = self.peakOut(obs_values["TSRC1"])
            T2 = self.peakOut(obs_values["TSRC2"])
            T3 = self.peakOut(obs_values["TSRC3"])
            EL = self.peakOut(obs_values["EL"])

            #AZ = AZ  # AZ is not used right now, suppose not average?
            

            #not except the dat_filename exists, need remove the old one
            if os.path.exists(dat_filename):
                os.remove(dat_filename)

            """
            dat file format:
            1.25 1.50 T0 --> 1.25GHz away from 183.3GHz(from the fit amc files "ifspec dsb 183.3 GHz"),
                         --> 1.50GHz bandwidth, T0 is the average value of TSRC0
            """
            with open(dat_filename,'w+') as f:
                #print('writing on '+ dat_filename)
                f.write('1.25 1.50 {0}\n'.format(T0))
                f.write('3.25 2.50 {0}\n'.format(T1))
                f.write('5.5 2.00 {0}\n'.format(T2))
                f.write('7.25 1.50 {0}'.format(T3))
                #print(f'{time} dat writing done.')
            f.close() 

            zen = 90 - EL  # calculate zenith angle to elevation

            #call the dat2Am function to create amc;ams;amr files
            self.dat2Am(am_temp_inp = am_temp_4dat, dat_fn_inp=dat_filename, zen_ang=zen, path=path)

            if path is not None:
                self.remove_old_files(path_save = path) #to save space for my laptop
            else:
                self.remove_old_files("") #to save space for my laptop

            end = perf_counter()

            time_taken = end - start  # calculate the time taken to process the file

            #save the time taken to csv file        
            self.timeTake(time_name, time_taken)

            num4Time += 1

            print(f"num of {num4Time} dat files done")

            if num4Time >= 1:
                continue
                #break  # for testing, remove this line to process all times
    
    def cleanCSV(self):
        """
        purpose:
            This function removes old CSV files.
        """

        time_take_file = self.time_take_file
        date_pwv_file = self.date_pwv_file

        try:
            os.remove(time_take_file)
            os.remove(date_pwv_file)
            print("Old csv files removed.")
        except Exception as e:
            print("No old csv files to remove.")

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
                file = file.split('\\')[-1]  # get the filename only
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

        self.cleanCSV()  # clean old csv files

        path_save = self.path_save  # path to save the results

        if self.get_slow_FNs_glob:
            # get the slow scan azimuth filenames if {get_slow_FNs_glob} is True
            sAz_slow_FNs = self.getsAzSlowFilenames()
        else:
            sAz_slow_FNs = self.sAz_slow_FNs

        am_temp_inp = self.am_temp  # default am template file

        for sAz_slow_FN in sAz_slow_FNs:
            
            self.slow2Dat(path = path_save, scanAz_slow_filename = sAz_slow_FN, am_temp = am_temp_inp)

    def sum_time_take(self):
        """
        purpose:
            sum the time taken for each TIME in the time_take.csv file
        """

        time_take_file = self.time_take_file

        total_time = 0

        with open(time_take_file, 'r') as t:
            next(t)  # skip header
            for line in t:
                parts = line.split(',')
                if len(parts) == 2:
                    total_time += float(parts[1])
        t.close()

        with open(time_take_file, 'a') as t:
            t.write(f"\nTotal time taken: {total_time:.4f} seconds\n")
        t.close()

        print(f"Total time taken: {total_time:.4f} seconds")

    #sum_time_take()  # sum the time 

if __name__ == "__main__":
    doFit = slow2FitPWV()
    doFit.date_pwv_file = 'time_pwv.csv'  # file to save the date and PWV values
    doFit.time_take_file = 'time_take.csv'  # file to save the time taken for each TIME
    doFit.am_temp = "SPole_annual_50.amc"  # am fit template file
    doFit.run()  # run the main function
    doFit.sum_time_take()  # sum the time taken for each dat file
    #print("All done.")
