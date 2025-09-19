"""
Ver 1.0 
combine scanAZ_*.py and recordProperty.py
remove average of data in scanAZ_*.py

"""

import os
import numpy as np
from typing import Dict
from time import perf_counter
from datetime import datetime
import glob
from time import sleep
import statistics as stats
from py2csv import timeTake, cleanCSV, sum_time_take
import pandas as pd
import time as t_fun

class slow2FitPWV:
    """
    A class to handle the slow scan Azimuth data and the fit PWV values using am fits.  

    How this class works:
        0. Initialize the class
        1. run method
            1.1 clean the old csv files bc we going to create new ones
            1.2 if get_slow_FNs_glob is True, get the slow scan azimuth filenames by glob package
            1.3 for each filename call the slow2Dat method
        2. slow2Dat method
            2.1 if {path_save} not None join the path to inputs FNs
            2.2 use {out_dict} to save the data read from the file
            2.3 call timeTake method to save the time taken to read the file
            2.4 for each TIME key in {out_dict}, create a dat file
                2.4.1 call peakOut method to find the extreme peak in the values
            2.5 call dat2Am method to create am files based on the dat file
            2.6 call remove_old_files method to remove old am files to save space
            2.7 The if-break of num4Time only for testing
        3. dat2Am method
            3.1 call am command to create am files based on the dat file (os.system)
            3.2 rewrite the {time} to remove the folders' name
            3.3 call read_am method to write to time_pwv.csv file based on the amc file
        4. read_am methods
            4.1 read the *.dat.amc files
            4.2 save to time_pwv.csv file

    Necessary methods:
        step 0: __init__: initialize the class with default values
        step 1: run: main function to run the process
        step 2: slow2Dat: read the *_scanAz_slow.txt file and write a dat file
        step 3: dat2Am: use the am fits to create amc;ams;amr files based on the dat file
        step 4: read_am: read the *.dat.amc files and write to time_pwv.csv file

    Math methods:
        
        peakOut: find the extreme peak(more than 50%) in a list of numbers, and remove it to give a new average number.

    Helpful methods:
        
        getsAzSlowFilenames: get the list of slow scan azimuth filenames by glob
    
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
        self.save_arr = []  # to save the results for each TIME
        self.npy_name = "Proyymm.npy"  # the name of the npy file to save the results

        self.num2Process = 315  # the number of TIME keys to process at a time (5 min)
        self.path_save = "results/"
        self.sAz_slow_FNs = []
        self.get_slow_FNs_glob = True # whether to get the scan azimuth slow filenames by the function using glob
        self.am_temp = "SPole_annual_50.amc"
        self.time_take_file = 'time_take.csv'  # file to save the time taken for each TIME
        self.date_pwv_file = 'time_pwv.csv'  # file to save the date and PWV values
        #self.percentage = 0.3  # percentage to find the extreme peak, default is 30%
 
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
        #print("in read_am")

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
        #print("in 2am")
        
        #When os is Linux need change *_inp name format
        if os.name == 'posix':
            if "\\" in am_temp_inp:
                am_temp_inp = am_temp_inp.replace('\\', '/')
            if "\\" in dat_fn_inp:
                dat_fn_inp = dat_fn_inp.replace('\\', '/')
            
        #print(f"{dat_fn_inp} created using {am_temp_inp} at zenith angle {zen_ang} degrees.")
        try:
            #print(f"Running am {am_temp_inp} {zen_ang} {dat_fn_inp}")
            os.system(f"am {am_temp_inp} {zen_ang} {dat_fn_inp}") 
            #print(f"am command done for {dat_fn_inp}")       
        except Exception as e:
            #print(f"Error in am command: {e}")
            timeTake(
                time_event_name=f"am command failed {am_temp_inp} {zen_ang} {dat_fn_inp} {e}",
                time_taken=0,
                time_take_file=self.time_take_file
            )

        sleep(0.1) #wait in case the system is slow

        try:
            #read the PWV from the new amc
            file_variable = open(dat_fn_inp+'.amc')
        except FileNotFoundError:
            #print(f"File not found: {dat_fn_inp+'.amc'}")
            timeTake(
                time_event_name=f"read amc file failed {dat_fn_inp}",
                time_taken=0,
                time_take_file=self.time_take_file
            )
            return

        all_lines_variable = file_variable.readlines()
        file_variable.close()

        #get the time from the dat_fn_inp
        time = dat_fn_inp
        if path is not None:
            # {time} except: "~/results/20250101S010147.191706E010156.795119_scanAz_slow.dat"
            time = os.path.basename(time)  # get the filename only
        time = time.split('_')[0]  

        # read the amc file and write to time_pwv.csv    
        self.read_am(all_lines_variable, time, zen_ang)  

    
        return

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

        new_f = []

        with open(scanAz_slow_filename, 'r') as f:
            # Read the file line by line
            for line in f:
                if line.startswith('#'):
                    continue
                split_rows = line.split()
                new_f.append(split_rows)

        df = pd.DataFrame(new_f)

        read_time_end = perf_counter()  # end the timer for reading the file

        time_taken = read_time_end - read_time_start  # calculate the time taken to read the file
        
        # save the time taken to the file
        timeTake(
            time_event_name=f"read {scanAz_slow_filename}",
            time_taken=time_taken,
            time_take_file=self.time_take_file
        )
        
        num4Time = 0 #to see how many done by py

        #A for loop to create the dat files based on diff TIME

        num2Pro = self.num2Process

        time = df[0][1:] #format: 2024-06-12T19:12:05.551599
        #timewvr = df[1][1:].astype(float)
        T0 = df[19][1:].astype(float)
        T1 = df[20][1:].astype(float)
        T2 = df[21][1:].astype(float)
        T3 = df[22][1:].astype(float)
        El = df[23][1:].astype(float)
        AZ = df[24][1:].astype(float)

        #convert {time} in local time to seconds since the Epoch
        T_since_Epo = np.zeros(len(time))
        for i in range(1, len(time)+1):
            time[i] = time[i].replace('T', ' ')
            print(time[i])
            T_since_Epo[i-1] = t_fun.mktime(t_fun.strptime(time[i], "%Y-%m-%d %H:%M:%S.%f"))

            
        if len(T_since_Epo) < 3420:
            #print("skip")
            return

        num2Pro = 315

        start = perf_counter()  # start the timer

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
            T0_median = np.median(T0_chunk)
            T0_std = np.std(T0_chunk)

            T1_chunk = T1[i:chunk_end]
            T1_max = np.max(T1_chunk)
            T1_min = np.min(T1_chunk)
            T1_avg = np.mean(T1_chunk)
            T1_median = np.median(T1_chunk)
            T1_std = np.std(T1_chunk)

            T2_chunk = T2[i:chunk_end]
            T2_max = np.max(T2_chunk)
            T2_min = np.min(T2_chunk)
            T2_avg = np.mean(T2_chunk)
            T2_median = np.median(T2_chunk)
            T2_std = np.std(T2_chunk)

            T3_chunk = T3[i:chunk_end]
            T3_max = np.max(T3_chunk)
            T3_min = np.min(T3_chunk)
            T3_avg = np.mean(T3_chunk)
            T3_median = np.median(T3_chunk)
            T3_std = np.std(T3_chunk)

            data_point = len(T0_chunk)

            self.save_arr.append([Time_start, Time_end, Time_avg, Time_leap, data_point, 
                            T0_max, T0_min, T0_avg, T0_median, T0_std, 
                            T1_max, T1_min, T1_avg, T1_median, T1_std,
                            T2_max, T2_min, T2_avg, T2_median, T2_std,
                            T3_max, T3_min, T3_avg, T3_median, T3_std
                            ]) 

            print(f"Processed TIME from {datetime.fromtimestamp(Time_start).strftime('%Y%m%dS%H%M%S.%fE')} to {datetime.fromtimestamp(Time_end).strftime('%Y%m%dS%H%M%S.%fE')} with {data_point} data points.")

            time_name = datetime.fromtimestamp(Time_start).strftime("%Y%m%dS%H%M%S.%fE") + datetime.fromtimestamp(Time_end).strftime("%H%M%S.%f")
            #write the dat filename based on the time
            dat_filename = f"{time_name}_scanAz_slow.dat"

            if path is not None:
                dat_filename = os.path.join(path, dat_filename)
            #not except the dat_filename exists, need remove the old one
            #?
            if os.path.exists(dat_filename):
                os.remove(dat_filename)

            """
            dat file format:
            1.25 1.50 T0 --> 1.25GHz away from 183.3GHz(from the fit amc files "ifspec dsb 183.3 GHz"),
                         --> 1.50GHz bandwidth, T0 is the average value of TSRC0
            """
            with open(dat_filename,'w+') as f:
                #print('writing on '+ dat_filename)
                f.write('1.25 1.50 {0}\n'.format(T0_avg))
                f.write('3.25 2.50 {0}\n'.format(T1_avg))
                f.write('5.5 2.00 {0}\n'.format(T2_avg))
                f.write('7.25 1.50 {0}'.format(T3_avg))
                #print(f'{time} dat writing done.')
            f.close() 
            
            El_avg = np.mean(El[i:chunk_end])
            zen = 90 - El_avg  # calculate zenith angle to elevation

            #call the dat2Am function to create amc;ams;amr files
            self.dat2Am(am_temp_inp = am_temp_4dat, dat_fn_inp=dat_filename, zen_ang=zen, path=path)

            end = perf_counter()

            time_taken = end - start  # calculate the time taken to process the file

            #save the time taken to csv file        
            timeTake(
                time_event_name=dat_filename,
                time_taken=time_taken,
                time_take_file=self.time_take_file
            )   

            #num4Time += 1

            #print(f"num of {num4Time} dat files done")

            #if num4Time >= 1:
                #continue
                #break  # for testing, remove this line to process all times


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
        if os.path.exists(self.date_pwv_file):
            cleanCSV(date_pwv_file=self.date_pwv_file)  # clean the old csv files

        path_save = self.path_save  # path to save the results

        if self.get_slow_FNs_glob:
            # get the slow scan azimuth filenames if {get_slow_FNs_glob} is True
            sAz_slow_FNs = self.getsAzSlowFilenames()
        else:
            sAz_slow_FNs = self.sAz_slow_FNs

        #let sAz_slow_FNs in the order of the time
        sAz_slow_FNs.sort()
        #print(sAz_slow_FNs)

        am_temp_inp = self.am_temp  # default am template file

        num4sAzFN = 0
        for sAz_slow_FN in sAz_slow_FNs:
            num4sAzFN += 1  # count the number of slow scan azimuth files processed            
            self.slow2Dat(path = path_save, scanAz_slow_filename = sAz_slow_FN, am_temp = am_temp_inp)
            #show number of time sAz_slow_FN processed
            print(f"Processed: {sAz_slow_FN} \n{num4sAzFN} in {len(sAz_slow_FNs)} slow scan azimuth files.")

        save_arr_np = np.array(self.save_arr)
        npy_name = self.path_save
        np.save(f"{npy_name}", save_arr_np)




if __name__ == "__main__":
    #How to use
    doFit = slow2FitPWV()
    doFit.num2Process = 300  # set the number of TIME keys to process at a time
    #doFit.percentage = 0.1  # set the percentage to find the extreme peak, default is 30%
    doFit.path_save = "results/" 
    doFit.date_pwv_file = f'time_pwv.csv'  # file to save the date and PWV values
    doFit.time_take_file = 'time_take.csv'  # file to save the time taken for each TIME
    doFit.am_temp = "SPole_annual_50.amc"  # am fit template file
    doFit.get_slow_FNs_glob = True
    #doFit.sAz_slow_FNs = ["20250101_010135_scanAz_slow.txt"]  # list of slow scan azimuth filenames
    cleanCSV(time_take_file=doFit.time_take_file, date_pwv_file=doFit.date_pwv_file)  # clean old csv files
    doFit.run()  # run the main function
    sum_time_take(doFit.time_take_file)  # sum the time taken for each TIME in the time_take.csv file
    print("All done.")
