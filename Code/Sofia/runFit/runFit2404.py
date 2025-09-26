"""
This code should also work for quasar
"""

import unzip
import scanAZ2 as scanAz
import py2csv

yymm = 2404  # file containing the month values

date_pwv_FN = f"time_pwv_{yymm}.csv"  # file to save the date and PWV values
#time_take_FN = "time_take.csv"  # file to save the time taken for each TIME
am_temp_FN = "SPole_annual_50.amc"  # am fit template file

path_data = f"results{yymm}/"  # Specify the path to the directory containing zip files

unzipper = unzip.unzipFiles(path_data)
unzipper.unzip_all = True
unzipper.am_temp = am_temp_FN  # Set the AM fit template file
unzipper.time_take_file = f"time_unzip_take{yymm}.csv"  # Set the time take file
#unzipper.delete_FN = False  # Set the flag to delete unneeded files
#py2csv.cleanCSV(time_take_file=unzipper.time_take_file)  # Clean old CSV files at the start
#unzipper.run_unzip()
#py2csv.sum_time_take(unzipper.time_take_file)

doFit = scanAz.slow2FitPWV()
#doFit.num2Process = 640  # set the number of TIME keys to process at a time
doFit.npy_name = f"Pro_{yymm}.npy"  # name the {yymm} npy file

doFit.path_save = path_data
doFit.date_pwv_file = date_pwv_FN  # file to save the date and PWV values
doFit.time_take_file = f"time_pwv_take{yymm}.csv" # file to save the time taken for each TIME
doFit.am_temp = am_temp_FN
#doFit.get_slow_FNs_glob = False
#doFit.sAz_slow_FNs = ["20240612_190135_scanAz_slow.txt"]
py2csv.cleanCSV(time_take_file=doFit.time_take_file, date_pwv_file=doFit.date_pwv_file)  # clean old csv files
doFit.run()  # run the main function
py2csv.sum_time_take(doFit.time_take_file)  # sum the time taken for each TIME in the time_take.csv file

print("All done.")
