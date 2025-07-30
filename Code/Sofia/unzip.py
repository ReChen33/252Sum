"""
25/07/29

Ver 2.1
    let archive failures not stop the process and record failures in time_take.csv

Ver 2.0
    import py2csv
    add functions for archive and delete files

Yifu

Purpose:
This code aim to unzip the files in the specified directory. 
Provide the data files scanAz_slow_2fit_pwv.py needed for the analysis.
Delete the other files that are not needed.

"""

import os
import zipfile
import tarfile
import glob
from time import perf_counter 
from time import sleep
from py2csv import timeTake 

class unzipFiles:
    def __init__(self, path):
        self.path = path  # Path to the directory containing zip files
        self.unzip_all = True  # Flag to control unzipping all files
        self.zip_files = []  # List to store zip files if needed
        self.am_temp = "SPole_annual_50.amc"  # AM fit template file
        self.time_take_file = "time_take.csv"

    def unzip_tar_gz(self, filename):
        if filename.endswith('.tar.gz'):
            tar_path = os.path.join(self.path, filename)
            
            try:
                with tarfile.open(tar_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(self.path, filter="data")
                    sleep(0.001)  # Sleep to ensure extraction is complete
                    print(f"Unzipped 1: {filename}")
                # Check if the tar file contains a tar.gz file
                    for member in tar_ref.getmembers():
                        if member.name.endswith('scanAz.tar.gz'):
                            inner_tar_path = os.path.join(self.path, member.name)
                            with tarfile.open(inner_tar_path, 'r:gz') as inner_tar_ref:
                                inner_tar_ref.extractall(self.path, filter="data")
                                #print(f"Unzipped inner tar.gz: {member.name}")
            except Exception as e:
                timeTake(
                    time_event_name=f"unzip failed {filename} {e}",
                    time_taken=0,
                    time_take_file=self.time_take_file
                )
                return 
            
    def unzip_zip(self, filename):
            if filename.endswith('.zip'):                
                zip_path = os.path.join(self.path, filename)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.path)
                print(f"Unzipped: {filename}")


    def run_unzip(self):

        if not self.unzip_all:
            if len(self.zip_files) == 0:
                return "No zip files to unzip."
        else:
            # Get all files in the specified directory
            self.zip_files = [f for f in os.listdir(self.path) 
                              if (f.endswith('.tar.gz') and ("_" not in f)) 
                              or f.endswith('.zip')]
            if len(self.zip_files) == 0:
                return "No zip files to unzip."

        for zip_file in self.zip_files:
            time_start = perf_counter()  # Start timing

            if zip_file.endswith('.tar.gz') and ("_" not in zip_file):
                self.unzip_tar_gz(zip_file)
            elif zip_file.endswith('.zip'):
                self.unzip_zip(zip_file)

            time_end = perf_counter()
            time_take = time_end - time_start

            time_take_FN = self.time_take_file

            timeTake(
                time_event_name=f"unzip {zip_file}",
                time_taken=time_take,
                time_take_file=time_take_FN
            )

            self.delete_unneeded_files()  # Call to delete unneeded files after unzipping
    
    def delete_unneeded_files(self):
        """
        use glob to find the files that are needed and delete the rest created files
        """

        delete_start = perf_counter()  # Start timing for deletion

        keep_files = []

        for zip_file in self.zip_files:
            zip_path = f"{self.path}{zip_file}"
            keep_path = [os.path.normpath(file) for file in glob.glob(zip_path)]
            keep_files.extend(keep_path)

        needed_path = f"{self.path}*scanAz_slow.txt"
        needed_files = glob.glob(needed_path)

        for needed_file in needed_files:
            needed_file = os.path.normpath(needed_file)  # Normalize the path
            keep_files.append(f"{needed_file}")
        #print(f"Keep files: {keep_files}")

        am_temp_path = f"{self.path}SPole_annual_50.amc"
        am_temp_file = os.path.normpath(am_temp_path)  # Normalize the path
        keep_files.append(am_temp_file)

        all_files = glob.glob(f"{self.path}*")
        all_files = [os.path.normpath(file) for file in all_files]

        for i in range(len(all_files)):
            if all_files[i] not in keep_files:
                try:
                    os.remove(all_files[i])
                except:
                    print(f"Failed to delete {all_files[i]}. ")
                    pass

        delete_end = perf_counter()
        delete_time = delete_end - delete_start

        timeTake(
            time_event_name="delete_unneeded_files",
            time_taken=delete_time,
            time_take_file=self.time_take_file
        )
                

if __name__ == "__main__":
    path_to_zip = "results/"  # Specify the path to the directory containing zip files
    unzipper = unzipFiles(path_to_zip)
    unzipper.unzip_all = True
    unzipper.am_temp = "SPole_annual_50.amc"
    #unzipper.zip_files = ["20250102.tar.gz", "20250131.zip"]  # Specify zip files to unzip
    unzipper.run_unzip()


    
