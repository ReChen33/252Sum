"""
This code should also work for quasar
"""

import unzip
import scanAz_slow_2fit_pwv as scanAz
import py2csv

date_pwv_FN = "time_pwv.csv"  # file to save the date and PWV values
#time_take_FN = "time_take.csv"  # file to save the time taken for each TIME
am_temp_FN = "SPole_annual_50.amc"  # am fit template file

path_data = "results/"  # Specify the path to the directory containing zip files
unzipper = unzip.unzipFiles(path_data)
unzipper.unzip_all = True
unzipper.am_temp = am_temp_FN  # Set the AM fit template file
unzipper.time_take_file = "time_unzip_take.csv"  # Set the time take file
py2csv.cleanCSV(time_take_file=unzipper.time_take_file)  # Clean old CSV files at the start
unzipper.run_unzip()
py2csv.sum_time_take(unzipper.time_take_file)

doFit = scanAz.slow2FitPWV()
doFit.num2Process = 640  # set the number of TIME keys to process at a time
doFit.path_save = path_data
doFit.date_pwv_file = date_pwv_FN  # file to save the date and PWV values
doFit.time_take_file = "time_pwv_take.csv" # file to save the time taken for each TIME
doFit.am_temp = am_temp_FN
py2csv.cleanCSV(time_take_file=doFit.time_take_file, date_pwv_file=doFit.date_pwv_file)  # clean old csv files
doFit.run()  # run the main function
py2csv.sum_time_take(doFit.time_take_file)  # sum the time taken for each TIME in the time_take.csv file

print("All done.")
