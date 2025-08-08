from main.IO import reading
from main.binning import bin
import glob

import csv
from main.binning.match_bins import get_mappers,apply_binners
import numpy as np
import sys
import os

from main.binning import bin_consts
import argparse
import main.IO.reading
from enum import Enum



def process(readpath : str, savepath : str, colNumsEnum : Enum):
    print(f"Starting on :{readpath}, saving to {savepath}")
    numerical_vals = reading.read_numerical_vals(readpath, colNumsEnum) #reading slow as not vectorised
    # print(numerical_vals)
    hitlocs = numerical_vals[:,1::]
    timestamps = numerical_vals[:,0]
    obj_names = reading.read_event_type(readpath, colNumsEnum) #reading slow as not vectorised
    # print("obj names")
    # for name in obj_names :
    #     if name != "Poster" and name not in bin_consts.OBJ_TO_BINNER :
    #         print(name)
    mappers = get_mappers(obj_names,hitlocs)
    print("Got mappers successfully")
    # print(mappers)
    print(np.nonzero([mappers == np.nan]))
    rel_bin_arr = apply_binners(mappers,hitlocs)
    print("Applied binners successfully")
    abs_bin_arr = bin.get_abs_bin(mappers, rel_bin_arr) # SLOW BECAUSE I HAVEN'T FIGURED OUT HOW TO VECTORISE THIS FULLY
    print("Converted relative to abs bin successfully")
    save_arr = np.hstack((timestamps.reshape(-1,1),abs_bin_arr.reshape(-1,1)))
    save_arr = save_arr[abs_bin_arr > 0, :]
    np.savetxt(savepath,save_arr,fmt='%d',delimiter=',')
    # with open(savepath, 'w', newline ='') as file :
    #     # writer = csv.writer(file)
    #     for i in range(numerical_vals.shape[0]) :
    #         #TODO : vectorise determination of binners DONE
    #         #TODO : modify binners to be vectorised DONE
    #         #TODO : vectorise feeding into binners DONE
    #         #TODO : vectorise conversion into offset DONE
    #         #TODO : check feeding into binners to make sure the output is in right format
    #         #TODO : check conversion into offset to make sure format agrees
            
    #         timestamp = numerical_vals[i,0]
    #         hitloc = numerical_vals[i,1::]
    #         # print(timestamp,hitloc)
    #         name = obj_names[i]
    #         out_data = (timestamp,bin.add_to_bin(name,hitloc))
    #         writer.writerow(out_data)
    print("all done")
    print(np.max(abs_bin_arr))

def get_savepath(path: str, is_multicast: bool = False) -> str:
    if (os.path.isdir(path)) :
        folder_path = path
    else:
        folder_path, _ = os.path.split(path)

    if is_multicast:
        # If it is multicast, append "_multicast" to the base name
        return os.path.join(folder_path,"mbinData.csv")

    return os.path.join(folder_path, f"1binData_new.csv")

    

def bin_path(path : str, multicast : bool, savepath : str) :
    # Use the provided path

    '''
    if os.path.isdir(path):
        # If a folder is passed, automatically search for both CSV files
        singlecast_path = os.path.join(path, 'unityfile_eyelink.csv')
        print(f"{singlecast_path}")
        multicast_path = os.path.join(path, 'unityfile_eyelink_multicast.csv')

        if os.path.exists(singlecast_path):
            print(f"Processing singlecast CSV file: {singlecast_path}")
            col_nums_enum = reading.colNumsSingleCast
            savepath = get_savepath(singlecast_path, is_multicast = False)
            process(singlecast_path, savepath, col_nums_enum)

        if os.path.exists(multicast_path):
            print("Processing multicast CSV file:")
            col_nums_enum = reading.colNumsMulticast
            savepath = get_savepath(multicast_path, is_multicast= True)
            process(multicast_path, savepath, col_nums_enum)
    
     else:
      '''
    # If a single file is passed, determine whether it is singlecast or multicast based on the flag
    if multicast:
        if not savepath : 
            savepath = get_savepath(path, is_multicast= True)
        
        col_nums_enum = reading.colNumsMulticast
    else:
        if not savepath : 
            savepath = get_savepath(path, is_multicast= False)
        
        col_nums_enum = reading.colNumsSingleCast

    print("Processing CSV file:")
    process(path, savepath, col_nums_enum)

def process_batch(batch_file_path: str):
    """Process multiple files listed in a text file"""
    with open(batch_file_path, 'r') as f:
        directory_paths = [line.strip() for line in f if line.strip()]
    
    for directory_path in directory_paths:
        if os.path.exists(directory_path) and os.path.isdir(directory_path):
            print(f"\n--- Searching in directory: {directory_path} ---")
            
            # Search for session*.csv files in the directory
            csv_pattern = os.path.join(directory_path, "session*.csv")
            csv_files = glob.glob(csv_pattern)
            
            if csv_files:
                print(f"Found {len(csv_files)} CSV file(s) matching pattern")
                for csv_file in csv_files:
                    print(f"\n--- Processing: {csv_file} ---")
                    try:
                        bin_path(path=csv_file, multicast=False, savepath=None)
                        print(f"✓ Successfully processed: {csv_file}")
                    except Exception as e:
                        print(f"✗ Error processing {csv_file}: {str(e)}")
            else:
                print(f"✗ No session*.csv files found in: {directory_path}")
        else:
            print(f"✗ Directory not found or invalid: {directory_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process CSV files.')
    
    parser.add_argument('--single_path', type=str, help='Path to the singlecast CSV')
    parser.add_argument('--multi_path', type=str, help="Path to the multicast CSV")
    parser.add_argument('--single_save_path', type=str, help="Path to save for single binning")
    parser.add_argument('--multi_save_path', type=str, help="Path to save for multi binning")
    parser.add_argument('--batch_file', type=str, help='Path to text file containing list of CSV paths to process')
    args = parser.parse_args()

    if args.batch_file:
        process_batch(args.batch_file)
    elif args.single_path:
        bin_path(path=args.single_path, multicast=False, savepath=args.single_save_path)
    else:
        print("Please provide either --single_path or --batch_file")
          
