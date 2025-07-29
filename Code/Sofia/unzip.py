"""
25/07/29

Ver 0.1
    created by: Yifu 07/29

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

class unzipFiles:
    def __init__(self, path):
        self.path = path  # Path to the directory containing zip files
        self.original_files = []  # List to store original files if needed
    
    def unzip_all(self):
        for filename in os.listdir(self.path):

            if filename.endswith('.tar.gz'):
                self.original_files.append(filename)  # Store original file names if needed
                tar_path = os.path.join(self.path, filename)
                os.system(f"tar -xzvf {tar_path} -C {self.path}")
                #!!! can improve !!!
                for file in os.listdir(self.path):
                    #print(f"Found file: {file}")
                    if file.endswith('scanAz.tar.gz'):
                        #self.original_files.append(file)  # Store original file names if needed
                        scan_path = os.path.join(self.path, file)
                        os.system(f"tar -xzvf {scan_path} -C {self.path}")

                print(f"Unzipped: {filename}")

            if filename.endswith('.zip'):
                self.original_files.append(filename)  # Store original file names if needed
                zip_path = os.path.join(self.path, filename)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.path)
                print(f"Unzipped: {filename}")
    
    def delete_unneeded_files(self):
        """
        use glob to find the files that are needed and delete the rest created files
        """
        keep_files = []

        for original_file in self.original_files:
            original_path = f"{self.path}{original_file}"
            #print(f"Original path: {original_path}")
            keep_path = [os.path.normpath(file) for file in glob.glob(original_path)]
            keep_files.extend(keep_path)

        needed_path = f"{self.path}*scanAz_slow.txt"
        needed_files = glob.glob(needed_path)
        for needed_file in needed_files:
            needed_file = os.path.normpath(needed_file)  # Normalize the path
            keep_files.append(f"{needed_file}")
        #print(f"Keep files: {keep_files}")

        all_files = glob.glob(f"{self.path}*")
        all_files = [os.path.normpath(file) for file in all_files]

        for i in range(len(all_files)):
            if all_files[i] not in keep_files:
                os.remove(all_files[i])
                #print(f"!Deleted: {all_files[i]}")

if __name__ == "__main__":
    path_to_zip = "data/"  # Specify the path to the directory containing zip files
    unzipper = unzipFiles(path_to_zip)
    unzipper.unzip_all()  # Unzip all files in the specified directory
    unzipper.delete_unneeded_files()  # Delete unneeded files
