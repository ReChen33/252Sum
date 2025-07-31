
import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict
from time import perf_counter
from datetime import datetime
import glob
from time import sleep
import statistics as stats
from py2csv import timeTake, cleanCSV, sum_time_take

class slow2FitPWV:

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
        #self.get_slow_FNs_glob = True # whether to get the scan azimuth slow filenames by the function using glob
        self.am_temp = "SPole_annual_50.amc"
        self.time_take_file = 'time_take.csv'  # file to save the time taken for each TIME
        self.date_pwv_file = 'time_pwv.csv'  # file to save the date and PWV values
        self.percentage = 0.3  # percentage to find the extreme peak, default is 30%


    def remove_old_files(self,path_save = "results/"):
        """"
        purpose:
        remove old .dat, .dat.amc, .dat.ams, and .dat.amr files in the specified path to save space
        """
        
        try:
            for file in glob.glob(f'{path_save}*.dat'):
                #print(f"Removing File: {file}")
                os.remove(file)
            for file in glob.glob(f'{path_save}*.dat.amc'):
                #print(f"Removing File: {file}")
                os.remove(file)
            for file in glob.glob(f'{path_save}*.dat.ams'):
                #print(f"Removing File: {file}")
                os.remove(file)
            for file in glob.glob(f'{path_save}*.dat.amr'):
                #print(f"Removing File: {file}")
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
        
        #When os is Linux need change *_inp name format
        if os.name == 'posix':
            if "\\" in am_temp_inp:
                am_temp_inp = am_temp_inp.replace('\\', '/')
            if "\\" in dat_fn_inp:
                dat_fn_inp = dat_fn_inp.replace('\\', '/')
            
        #print(f"{dat_fn_inp} created using {am_temp_inp} at zenith angle {zen_ang} degrees.")
        try:
            os.system(f"am {am_temp_inp} {zen_ang} {dat_fn_inp}")        
        except Exception as e:
            #print(f"Error in am command: {e}")
            timeTake(
                time_event_name=f"am command failed {am_temp_inp} {zen_ang} {dat_fn_inp} {e}",
                time_taken=0,
                time_take_file=self.time_take_file
            )

        sleep(0.001) #wait in case the system is slow

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


    def peakOut(self, numbers, percentage=0.3):
        
        """
        Purpose: 
            Find the extreme peak(more than {percentage}) in a list of numbers, and remove it to give a new average number.

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
        timeTake(
            time_event_name=f"read {scanAz_slow_filename}",
            time_taken=time_taken,
            time_take_file=self.time_take_file
        )

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

            percentage = self.percentage  # percentage to find the extreme peak, default is 30%
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

            # if path is not None:
            #     self.remove_old_files(path_save = path) #to save space for my laptop
            # else:
            #     self.remove_old_files("") #to save space for my laptop

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
            print("Not use this part")
            # get the slow scan azimuth filenames if {get_slow_FNs_glob} is True
            #sAz_slow_FNs = self.getsAzSlowFilenames()
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




if __name__ == "__main__":
    #How to use
    doFit = slow2FitPWV()
    doFit.num2Process = 640  # set the number of TIME keys to process at a time
    #doFit.percentage = 0.1  # set the percentage to find the extreme peak, default is 30%
    doFit.path_save = "results/" 
    doFit.date_pwv_file = f'time_pwv_2402.csv'  # file to save the date and PWV values
    doFit.time_take_file = 'time_pwv_take2402.csv'  # file to save the time taken for each TIME
    doFit.am_temp = "SPole_annual_50.amc"  # am fit template file
    doFit.get_slow_FNs_glob = False
    doFit.sAz_slow_FNs = [
        '20240201_010134_scanAz_slow.txt', 
        '20240201_020134_scanAz_slow.txt', 
        '20240201_030134_scanAz_slow.txt', 
        '20240201_050134_scanAz_slow.txt', 
        '20240201_060135_scanAz_slow.txt', 
        '20240201_070135_scanAz_slow.txt', 
        '20240201_090134_scanAz_slow.txt', 
        '20240201_100134_scanAz_slow.txt', 
        '20240201_110135_scanAz_slow.txt', 
        '20240201_130135_scanAz_slow.txt', 
        '20240201_140135_scanAz_slow.txt', 
        '20240201_150134_scanAz_slow.txt', 
        '20240201_170134_scanAz_slow.txt', 
        '20240201_180135_scanAz_slow.txt', 
        '20240201_190135_scanAz_slow.txt', 
        '20240201_210135_scanAz_slow.txt', 
        '20240201_220134_scanAz_slow.txt', 
        '20240202_010135_scanAz_slow.txt', 
        '20240202_020135_scanAz_slow.txt', 
        '20240202_030135_scanAz_slow.txt', 
        '20240202_050134_scanAz_slow.txt', 
        '20240202_060134_scanAz_slow.txt', 
        '20240202_070135_scanAz_slow.txt', 
        '20240202_090135_scanAz_slow.txt', 
        '20240202_100135_scanAz_slow.txt', 
        '20240202_110134_scanAz_slow.txt', 
        '20240202_130134_scanAz_slow.txt', 
        '20240202_140135_scanAz_slow.txt', 
        '20240202_150135_scanAz_slow.txt', 
        '20240202_170135_scanAz_slow.txt', 
        '20240202_180134_scanAz_slow.txt', 
        '20240202_190134_scanAz_slow.txt', 
        '20240202_210135_scanAz_slow.txt', 
        '20240202_220135_scanAz_slow.txt', 
        '20240203_010134_scanAz_slow.txt', 
        '20240203_020134_scanAz_slow.txt', 
        '20240203_030135_scanAz_slow.txt', 
        '20240203_050135_scanAz_slow.txt', 
        '20240203_060135_scanAz_slow.txt', 
        '20240203_070134_scanAz_slow.txt', 
        '20240203_090134_scanAz_slow.txt', 
        '20240203_100135_scanAz_slow.txt', 
        '20240203_110135_scanAz_slow.txt', 
        '20240203_130135_scanAz_slow.txt', 
        '20240203_140134_scanAz_slow.txt', 
        '20240203_150134_scanAz_slow.txt', 
        '20240203_170134_scanAz_slow.txt', 
        '20240203_180135_scanAz_slow.txt', 
        '20240203_190135_scanAz_slow.txt', 
        '20240203_210134_scanAz_slow.txt', 
        '20240203_220134_scanAz_slow.txt', 
        '20240204_010135_scanAz_slow.txt', 
        '20240204_020135_scanAz_slow.txt', 
        '20240204_030135_scanAz_slow.txt', 
        '20240204_050134_scanAz_slow.txt', 
        '20240204_060134_scanAz_slow.txt', 
        '20240204_070135_scanAz_slow.txt', 
        '20240204_090135_scanAz_slow.txt', 
        '20240204_100135_scanAz_slow.txt', 
        '20240204_110134_scanAz_slow.txt', 
        '20240204_130134_scanAz_slow.txt', 
        '20240204_140134_scanAz_slow.txt', 
        '20240204_150135_scanAz_slow.txt', 
        '20240204_170135_scanAz_slow.txt', 
        '20240204_180135_scanAz_slow.txt', 
        '20240204_190134_scanAz_slow.txt', 
        '20240204_210134_scanAz_slow.txt', 
        '20240204_220135_scanAz_slow.txt', 
        '20240205_010135_scanAz_slow.txt', 
        '20240205_020134_scanAz_slow.txt', 
        '20240205_030134_scanAz_slow.txt', 
        '20240205_050135_scanAz_slow.txt', 
        '20240205_060135_scanAz_slow.txt', 
        '20240205_070135_scanAz_slow.txt', 
        '20240205_090134_scanAz_slow.txt', 
        '20240205_100134_scanAz_slow.txt', 
        '20240205_110135_scanAz_slow.txt', 
        '20240205_130135_scanAz_slow.txt', 
        '20240205_140134_scanAz_slow.txt', 
        '20240205_150134_scanAz_slow.txt', 
        '20240205_170134_scanAz_slow.txt', 
        '20240205_180135_scanAz_slow.txt', 
        '20240205_190135_scanAz_slow.txt', 
        '20240205_210135_scanAz_slow.txt', 
        '20240205_220134_scanAz_slow.txt', 
        '20240206_010135_scanAz_slow.txt', 
        '20240206_020135_scanAz_slow.txt', 
        '20240206_030135_scanAz_slow.txt', 
        '20240206_050134_scanAz_slow.txt', 
        '20240206_060134_scanAz_slow.txt', 
        '20240206_070135_scanAz_slow.txt', 
        '20240206_090135_scanAz_slow.txt', 
        '20240206_100135_scanAz_slow.txt', 
        '20240206_110134_scanAz_slow.txt', 
        '20240206_130134_scanAz_slow.txt', 
        '20240206_140135_scanAz_slow.txt', 
        '20240206_150135_scanAz_slow.txt', 
        '20240206_170135_scanAz_slow.txt', 
        '20240206_180134_scanAz_slow.txt', 
        '20240206_190134_scanAz_slow.txt', 
        '20240206_210134_scanAz_slow.txt', 
        '20240206_220135_scanAz_slow.txt', 
        '20240207_010135_scanAz_slow.txt', 
        '20240207_020134_scanAz_slow.txt', 
        '20240207_030134_scanAz_slow.txt', 
        '20240207_050135_scanAz_slow.txt', 
        '20240207_060135_scanAz_slow.txt', 
        '20240207_070135_scanAz_slow.txt', 
        '20240207_090134_scanAz_slow.txt', 
        '20240207_100134_scanAz_slow.txt', 
        '20240207_110135_scanAz_slow.txt', 
        '20240207_130135_scanAz_slow.txt', 
        '20240207_140135_scanAz_slow.txt', 
        '20240207_150134_scanAz_slow.txt', 
        '20240207_170134_scanAz_slow.txt', 
        '20240207_180134_scanAz_slow.txt', 
        '20240207_190135_scanAz_slow.txt', 
        '20240207_210135_scanAz_slow.txt', 
        '20240207_220135_scanAz_slow.txt', 
        '20240208_010134_scanAz_slow.txt', 
        '20240208_020134_scanAz_slow.txt', 
        '20240208_030135_scanAz_slow.txt', 
        '20240208_050135_scanAz_slow.txt', 
        '20240208_060135_scanAz_slow.txt', 
        '20240208_070134_scanAz_slow.txt', 
        '20240208_090134_scanAz_slow.txt', 
        '20240208_100135_scanAz_slow.txt', 
        '20240208_110135_scanAz_slow.txt', 
        '20240208_130135_scanAz_slow.txt', 
        '20240208_140134_scanAz_slow.txt', 
        '20240208_150134_scanAz_slow.txt', 
        '20240208_170135_scanAz_slow.txt', 
        '20240208_180135_scanAz_slow.txt', 
        '20240208_190135_scanAz_slow.txt', 
        '20240208_210134_scanAz_slow.txt', 
        '20240208_220134_scanAz_slow.txt', 
        '20240209_010135_scanAz_slow.txt', 
        '20240209_020135_scanAz_slow.txt', 
        '20240209_030134_scanAz_slow.txt', 
        '20240209_050134_scanAz_slow.txt', 
        '20240209_060135_scanAz_slow.txt', 
        '20240209_070135_scanAz_slow.txt', 
        '20240209_090135_scanAz_slow.txt', 
        '20240209_100134_scanAz_slow.txt', 
        '20240209_110134_scanAz_slow.txt', 
        '20240209_130134_scanAz_slow.txt', 
        '20240209_140135_scanAz_slow.txt', 
        '20240209_150135_scanAz_slow.txt', 
        '20240209_170134_scanAz_slow.txt', 
        '20240209_180134_scanAz_slow.txt', 
        '20240209_190135_scanAz_slow.txt', 
        '20240209_210135_scanAz_slow.txt', 
        '20240209_220135_scanAz_slow.txt', 
        '20240210_010134_scanAz_slow.txt', 
        '20240210_020134_scanAz_slow.txt', 
        '20240210_030135_scanAz_slow.txt', 
        '20240210_050135_scanAz_slow.txt', 
        '20240210_060134_scanAz_slow.txt', 
        '20240210_070134_scanAz_slow.txt', 
        '20240210_090134_scanAz_slow.txt', 
        '20240210_100135_scanAz_slow.txt', 
        '20240210_110135_scanAz_slow.txt', 
        '20240210_130135_scanAz_slow.txt', 
        '20240210_140134_scanAz_slow.txt', 
        '20240210_150134_scanAz_slow.txt', 
        '20240210_170135_scanAz_slow.txt', 
        '20240210_180135_scanAz_slow.txt', 
        '20240210_190135_scanAz_slow.txt', 
        '20240210_210134_scanAz_slow.txt', 
        '20240210_220134_scanAz_slow.txt', 
        '20240211_010135_scanAz_slow.txt', 
        '20240211_020135_scanAz_slow.txt', 
        '20240211_030134_scanAz_slow.txt', 
        '20240211_050134_scanAz_slow.txt', 
        '20240211_060135_scanAz_slow.txt', 
        '20240211_070135_scanAz_slow.txt', 
        '20240211_090135_scanAz_slow.txt', 
        '20240211_100134_scanAz_slow.txt', 
        '20240211_110134_scanAz_slow.txt', 
        '20240211_130135_scanAz_slow.txt', 
        '20240211_140135_scanAz_slow.txt', 
        '20240211_150135_scanAz_slow.txt', 
        '20240211_170134_scanAz_slow.txt', 
        '20240211_180134_scanAz_slow.txt', 
        '20240211_190135_scanAz_slow.txt', 
        '20240211_210135_scanAz_slow.txt', 
        '20240211_220135_scanAz_slow.txt', 
        '20240212_010134_scanAz_slow.txt', 
        '20240212_020134_scanAz_slow.txt', 
        '20240212_030135_scanAz_slow.txt', 
        '20240212_050135_scanAz_slow.txt', 
        '20240212_060135_scanAz_slow.txt', 
        '20240212_070134_scanAz_slow.txt', 
        '20240212_090134_scanAz_slow.txt', 
        '20240212_100135_scanAz_slow.txt', 
        '20240212_110135_scanAz_slow.txt', 
        '20240212_130135_scanAz_slow.txt', 
        '20240212_140134_scanAz_slow.txt', 
        '20240212_150134_scanAz_slow.txt', 
        '20240212_170134_scanAz_slow.txt', 
        '20240212_180135_scanAz_slow.txt', 
        '20240212_190135_scanAz_slow.txt', 
        '20240212_210134_scanAz_slow.txt', 
        '20240212_220134_scanAz_slow.txt', 
        '20240213_010135_scanAz_slow.txt', 
        '20240213_020135_scanAz_slow.txt', 
        '20240213_030135_scanAz_slow.txt', 
        '20240213_050134_scanAz_slow.txt', 
        '20240213_060134_scanAz_slow.txt', 
        '20240213_070135_scanAz_slow.txt', 
        '20240213_090135_scanAz_slow.txt', 
        '20240213_100135_scanAz_slow.txt', 
        '20240213_110134_scanAz_slow.txt', 
        '20240213_130134_scanAz_slow.txt', 
        '20240213_140135_scanAz_slow.txt', 
        '20240213_150135_scanAz_slow.txt', 
        '20240213_170135_scanAz_slow.txt', 
        '20240213_180134_scanAz_slow.txt', 
        '20240213_190134_scanAz_slow.txt', 
        '20240213_210135_scanAz_slow.txt', 
        '20240213_220135_scanAz_slow.txt', 
        '20240214_010134_scanAz_slow.txt', 
        '20240214_020134_scanAz_slow.txt', 
        '20240214_030135_scanAz_slow.txt', 
        '20240214_050135_scanAz_slow.txt', 
        '20240214_060135_scanAz_slow.txt', 
        '20240214_070134_scanAz_slow.txt', 
        '20240214_090134_scanAz_slow.txt', 
        '20240214_100135_scanAz_slow.txt', 
        '20240214_110135_scanAz_slow.txt', 
        '20240214_130135_scanAz_slow.txt', 
        '20240214_140134_scanAz_slow.txt', 
        '20240214_150134_scanAz_slow.txt', 
        '20240214_170134_scanAz_slow.txt', 
        '20240214_180135_scanAz_slow.txt', 
        '20240214_190135_scanAz_slow.txt', 
        '20240214_210135_scanAz_slow.txt', 
        '20240214_220134_scanAz_slow.txt', 
        '20240215_010135_scanAz_slow.txt', 
        '20240215_020135_scanAz_slow.txt', 
        '20240215_030135_scanAz_slow.txt', 
        '20240215_050134_scanAz_slow.txt', 
        '20240215_060134_scanAz_slow.txt', 
        '20240215_070134_scanAz_slow.txt', 
        '20240215_090135_scanAz_slow.txt', 
        '20240215_100135_scanAz_slow.txt', 
        '20240215_110134_scanAz_slow.txt', 
        '20240215_130134_scanAz_slow.txt', 
        '20240215_140135_scanAz_slow.txt', 
        '20240215_150135_scanAz_slow.txt', 
        '20240215_170135_scanAz_slow.txt', 
        '20240215_180135_scanAz_slow.txt', 
        '20240215_190134_scanAz_slow.txt', 
        '20240215_210134_scanAz_slow.txt', 
        '20240215_220135_scanAz_slow.txt', 
        '20240216_010135_scanAz_slow.txt', 
        '20240216_020134_scanAz_slow.txt', 
        '20240216_030134_scanAz_slow.txt', 
        '20240216_050135_scanAz_slow.txt', 
        '20240216_060135_scanAz_slow.txt', 
        '20240216_070135_scanAz_slow.txt', 
        '20240216_090134_scanAz_slow.txt', 
        '20240216_100134_scanAz_slow.txt', 
        '20240216_110135_scanAz_slow.txt', 
        '20240216_130135_scanAz_slow.txt', 
        '20240216_140134_scanAz_slow.txt', 
        '20240216_150134_scanAz_slow.txt', 
        '20240216_170134_scanAz_slow.txt', 
        '20240216_180135_scanAz_slow.txt', 
        '20240216_190135_scanAz_slow.txt', 
        '20240216_210134_scanAz_slow.txt', 
        '20240216_220134_scanAz_slow.txt', 
        '20240217_010135_scanAz_slow.txt', 
        '20240217_020135_scanAz_slow.txt', 
        '20240217_030134_scanAz_slow.txt', 
        '20240217_050134_scanAz_slow.txt', 
        '20240217_060134_scanAz_slow.txt', 
        '20240217_070135_scanAz_slow.txt', 
        '20240217_090135_scanAz_slow.txt', 
        '20240217_100134_scanAz_slow.txt', 
        '20240217_110134_scanAz_slow.txt', 
        '20240217_130134_scanAz_slow.txt', 
        '20240217_140135_scanAz_slow.txt', 
        '20240217_150135_scanAz_slow.txt', 
        '20240217_170134_scanAz_slow.txt', 
        '20240217_180134_scanAz_slow.txt', 
        '20240217_190134_scanAz_slow.txt', 
        '20240217_210135_scanAz_slow.txt', 
        '20240217_220135_scanAz_slow.txt', 
        '20240218_010134_scanAz_slow.txt', 
        '20240218_020134_scanAz_slow.txt', 
        '20240218_030135_scanAz_slow.txt', 
        '20240218_050135_scanAz_slow.txt', 
        '20240218_060135_scanAz_slow.txt', 
        '20240218_070134_scanAz_slow.txt', 
        '20240218_090134_scanAz_slow.txt', 
        '20240218_100135_scanAz_slow.txt', 
        '20240218_110135_scanAz_slow.txt', 
        '20240218_130134_scanAz_slow.txt', 
        '20240218_140134_scanAz_slow.txt', 
        '20240218_150134_scanAz_slow.txt', 
        '20240218_170135_scanAz_slow.txt', 
        '20240218_180135_scanAz_slow.txt', 
        '20240218_190134_scanAz_slow.txt', 
        '20240218_210134_scanAz_slow.txt', 
        '20240218_220134_scanAz_slow.txt', 
        '20240219_010135_scanAz_slow.txt', 
        '20240219_020135_scanAz_slow.txt', 
        '20240219_030134_scanAz_slow.txt', 
        '20240219_050134_scanAz_slow.txt', 
        '20240219_060135_scanAz_slow.txt', 
        '20240219_070135_scanAz_slow.txt', 
        '20240219_090135_scanAz_slow.txt', 
        '20240219_100134_scanAz_slow.txt', 
        '20240219_110134_scanAz_slow.txt', 
        '20240219_130135_scanAz_slow.txt', 
        '20240219_140135_scanAz_slow.txt', 
        '20240219_150135_scanAz_slow.txt', 
        '20240219_170135_scanAz_slow.txt', 
        '20240219_180134_scanAz_slow.txt', 
        '20240219_190134_scanAz_slow.txt', 
        '20240219_210135_scanAz_slow.txt', 
        '20240219_220135_scanAz_slow.txt', 
        '20240220_010134_scanAz_slow.txt', 
        '20240220_020134_scanAz_slow.txt', 
        '20240220_030135_scanAz_slow.txt', 
        '20240220_050135_scanAz_slow.txt', 
        '20240220_060135_scanAz_slow.txt', 
        '20240220_070134_scanAz_slow.txt', 
        '20240220_090134_scanAz_slow.txt', 
        '20240220_100135_scanAz_slow.txt', 
        '20240220_110135_scanAz_slow.txt', 
        '20240220_130135_scanAz_slow.txt', 
        '20240220_140134_scanAz_slow.txt', 
        '20240220_150134_scanAz_slow.txt', 
        '20240220_170134_scanAz_slow.txt', 
        '20240220_180135_scanAz_slow.txt', 
        '20240220_190135_scanAz_slow.txt', 
        '20240220_210135_scanAz_slow.txt', 
        '20240220_220134_scanAz_slow.txt', 
        '20240221_010135_scanAz_slow.txt', 
        '20240221_020135_scanAz_slow.txt', 
        '20240221_030135_scanAz_slow.txt', 
        '20240221_050134_scanAz_slow.txt', 
        '20240221_060134_scanAz_slow.txt', 
        '20240221_070134_scanAz_slow.txt', 
        '20240221_090135_scanAz_slow.txt', 
        '20240221_100135_scanAz_slow.txt', 
        '20240221_110134_scanAz_slow.txt', 
        '20240221_130134_scanAz_slow.txt', 
        '20240221_140135_scanAz_slow.txt', 
        '20240221_150135_scanAz_slow.txt', 
        '20240221_170135_scanAz_slow.txt', 
        '20240221_180134_scanAz_slow.txt', 
        '20240221_190134_scanAz_slow.txt', 
        '20240221_210134_scanAz_slow.txt', 
        '20240221_220135_scanAz_slow.txt', 
        '20240222_010135_scanAz_slow.txt', 
        '20240222_020134_scanAz_slow.txt', 
        '20240222_030134_scanAz_slow.txt', 
        '20240222_050135_scanAz_slow.txt', 
        '20240222_060135_scanAz_slow.txt', 
        '20240222_070135_scanAz_slow.txt', 
        '20240222_090134_scanAz_slow.txt', 
        '20240222_100134_scanAz_slow.txt', 
        '20240222_110135_scanAz_slow.txt', 
        '20240222_130135_scanAz_slow.txt', 
        '20240222_140134_scanAz_slow.txt', 
        '20240222_150134_scanAz_slow.txt', 
        '20240222_170134_scanAz_slow.txt', 
        '20240222_180135_scanAz_slow.txt', 
        '20240222_190135_scanAz_slow.txt', 
        '20240222_210135_scanAz_slow.txt', 
        '20240222_220134_scanAz_slow.txt', 
        '20240223_010135_scanAz_slow.txt', 
        '20240223_020135_scanAz_slow.txt', 
        '20240223_030135_scanAz_slow.txt', 
        '20240223_050134_scanAz_slow.txt', 
        '20240223_060134_scanAz_slow.txt', 
        '20240223_070135_scanAz_slow.txt', 
        '20240223_090135_scanAz_slow.txt', 
        '20240223_100135_scanAz_slow.txt', 
        '20240223_110134_scanAz_slow.txt', 
        '20240223_130134_scanAz_slow.txt', 
        '20240223_140135_scanAz_slow.txt', 
        '20240223_150135_scanAz_slow.txt', 
        '20240223_170135_scanAz_slow.txt', 
        '20240223_180134_scanAz_slow.txt', 
        '20240223_190134_scanAz_slow.txt', 
        '20240223_210134_scanAz_slow.txt', 
        '20240223_220135_scanAz_slow.txt', 
        '20240224_010134_scanAz_slow.txt', 
        '20240224_020134_scanAz_slow.txt', 
        '20240224_030134_scanAz_slow.txt', 
        '20240224_050135_scanAz_slow.txt', 
        '20240224_060135_scanAz_slow.txt', 
        '20240224_070134_scanAz_slow.txt', 
        '20240224_090134_scanAz_slow.txt', 
        '20240224_100134_scanAz_slow.txt', 
        '20240224_110135_scanAz_slow.txt', 
        '20240224_130135_scanAz_slow.txt', 
        '20240224_140135_scanAz_slow.txt', 
        '20240224_150134_scanAz_slow.txt', 
        '20240224_170134_scanAz_slow.txt', 
        '20240224_180135_scanAz_slow.txt', 
        '20240224_190135_scanAz_slow.txt', 
        '20240224_210135_scanAz_slow.txt', 
        '20240224_220134_scanAz_slow.txt', 
        '20240225_010134_scanAz_slow.txt', 
        '20240225_020135_scanAz_slow.txt', 
        '20240225_030135_scanAz_slow.txt', 
        '20240225_050135_scanAz_slow.txt', 
        '20240225_060134_scanAz_slow.txt', 
        '20240225_070134_scanAz_slow.txt', 
        '20240225_090135_scanAz_slow.txt', 
        '20240225_100135_scanAz_slow.txt', 
        '20240225_110135_scanAz_slow.txt', 
        '20240225_130134_scanAz_slow.txt', 
        '20240225_140134_scanAz_slow.txt', 
        '20240225_150135_scanAz_slow.txt', 
        '20240225_170135_scanAz_slow.txt', 
        '20240225_180135_scanAz_slow.txt', 
        '20240225_190134_scanAz_slow.txt', 
        '20240225_210134_scanAz_slow.txt', 
        '20240225_220134_scanAz_slow.txt', 
        '20240226_010135_scanAz_slow.txt', 
        '20240226_020135_scanAz_slow.txt', 
        '20240226_030134_scanAz_slow.txt', 
        '20240226_050134_scanAz_slow.txt', 
        '20240226_060134_scanAz_slow.txt', 
        '20240226_070135_scanAz_slow.txt', 
        '20240226_090135_scanAz_slow.txt', 
        '20240226_100134_scanAz_slow.txt', 
        '20240226_110134_scanAz_slow.txt', 
        '20240226_130134_scanAz_slow.txt', 
        '20240226_140135_scanAz_slow.txt', 
        '20240226_150135_scanAz_slow.txt', 
        '20240226_170135_scanAz_slow.txt', 
        '20240226_180134_scanAz_slow.txt', 
        '20240226_190134_scanAz_slow.txt', 
        '20240226_210134_scanAz_slow.txt', 
        '20240226_220135_scanAz_slow.txt', 
        '20240227_010134_scanAz_slow.txt', 
        '20240227_020134_scanAz_slow.txt', 
        '20240227_030134_scanAz_slow.txt', 
        '20240227_050135_scanAz_slow.txt', 
        '20240227_060135_scanAz_slow.txt', 
        '20240227_070135_scanAz_slow.txt', 
        '20240227_090134_scanAz_slow.txt', 
        '20240227_100134_scanAz_slow.txt', 
        '20240227_110135_scanAz_slow.txt', 
        '20240227_130135_scanAz_slow.txt', 
        '20240227_140135_scanAz_slow.txt', 
        '20240227_150134_scanAz_slow.txt', 
        '20240227_170134_scanAz_slow.txt', 
        '20240227_180134_scanAz_slow.txt', 
        '20240227_190135_scanAz_slow.txt', 
        '20240227_210135_scanAz_slow.txt', 
        '20240227_220135_scanAz_slow.txt', 
        '20240228_010134_scanAz_slow.txt', 
        '20240228_020135_scanAz_slow.txt', 
        '20240228_030135_scanAz_slow.txt', 
        '20240228_050135_scanAz_slow.txt', 
        '20240228_060134_scanAz_slow.txt', 
        '20240228_070134_scanAz_slow.txt', 
        '20240228_090134_scanAz_slow.txt', 
        '20240228_100135_scanAz_slow.txt', 
        '20240228_110135_scanAz_slow.txt', 
        '20240228_130134_scanAz_slow.txt', 
        '20240228_140134_scanAz_slow.txt', 
        '20240228_150135_scanAz_slow.txt', 
        '20240228_170135_scanAz_slow.txt', 
        '20240228_180135_scanAz_slow.txt', 
        '20240228_190134_scanAz_slow.txt', 
        '20240228_210134_scanAz_slow.txt', 
        '20240228_220135_scanAz_slow.txt', 
        '20240229_010135_scanAz_slow.txt', 
        '20240229_020134_scanAz_slow.txt', 
        '20240229_030134_scanAz_slow.txt', 
        '20240229_050135_scanAz_slow.txt', 
        '20240229_060135_scanAz_slow.txt', 
        '20240229_070135_scanAz_slow.txt', 
        '20240229_090134_scanAz_slow.txt', 
        '20240229_100134_scanAz_slow.txt', 
        '20240229_110134_scanAz_slow.txt', 
        '20240229_130135_scanAz_slow.txt', 
        '20240229_140135_scanAz_slow.txt', 
        '20240229_150134_scanAz_slow.txt', 
        '20240229_170134_scanAz_slow.txt', 
        '20240229_180135_scanAz_slow.txt', 
        '20240229_190135_scanAz_slow.txt', 
        '20240229_210135_scanAz_slow.txt', 
        '20240229_220134_scanAz_slow.txt'
    ]  # list of slow scan azimuth filenames
    cleanCSV(time_take_file=doFit.time_take_file, date_pwv_file=doFit.date_pwv_file)  # clean old csv files
    doFit.run()  # run the main function
    doFit.remove_old_files(path_save=doFit.path_save)  # remove old files
    sum_time_take(doFit.time_take_file)  # sum the time taken for each TIME in the time_take.csv file
    #print("All done.")
