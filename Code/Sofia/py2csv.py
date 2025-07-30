"""
Yifu 
Ver 1.0

Purpose:
This code lets unzip.py and scanAz_slow_2fit_pwv.py share the CSV related functions.

timeTake: save the time taken for each event into the time_take.csv file
sum_time_take: sum the time taken for each time_event in the time_take.csv file
cleanCSV: remove old csv files
"""

import os


def timeTake(time_event_name, time_taken:float, time_take_file="time_take.csv"):
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

        time_take_FN = time_take_file

        #!!!logical change: the time_take file will be created in unzip.py
        if not os.path.exists(time_take_FN):
            with open(time_take_FN, 'w') as t:
                #In case the file does not exist
                t.write("TIME,take TIME (seconds)\n")
                t.write(f"{time_event_name},{time_taken:.4f}\n")
            t.close()
        else:
            with open(time_take_FN, 'a') as t:
                t.write(f"{time_event_name},{time_taken:.4f}\n")
            t.close()

def cleanCSV(time_take_file = None, date_pwv_file = None):
    """
    purpose:
        This function removes old CSV files.
    """
    try:
        if time_take_file is not None:
            os.remove(time_take_file)
            print(f"Old {time_take_file} file removed.")
    except Exception as e:
        print(f"Failed to remove {time_take_file}: {e}")

    try:        
        if date_pwv_file is not None:
            os.remove(date_pwv_file)
            print(f"Old {date_pwv_file} file removed.")
    except Exception as e:
        print(f"Failed to remove {date_pwv_file}: {e}")

def sum_time_take(time_take_file):
    """
    purpose:
        sum the time taken for each TIME in the time_take.csv file
    """

    total_time = 0

    with open(time_take_file, 'r+') as t:
        next(t)  # skip header
        total_time = 0.0
        for line in t:
            parts = line.split(',')
            if len(parts) == 2:
                total_time += float(parts[1])
        
        # Move to end of file to append
        t.write(f"\nTotal time taken: {total_time:.4f} seconds\n")
    t.close()  

    print(f"Total time taken: {total_time:.4f} seconds")