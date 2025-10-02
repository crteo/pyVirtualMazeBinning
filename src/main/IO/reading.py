from enum import Enum
import csv
import numpy as np
import pandas as pd

def read_data_with_masks(csv_path: str, colNumEnum: Enum):
    """
    Reads all necessary data (numerical, object names) and returns the 
    DataFrame along with the masks for validity and fixation end.
    """
    raycast_df = process_types(csv_path) #update samples with correct samples
    
    # 1. Mask for samples that are END of a fixation
    fixation_mask = raycast_df.iloc[:, 0].isin(["SAMPLEENDFIX"])
    
    # 2. Mask for samples with valid (non-NaN) coordinates
    valid_samples_mask = raycast_df.iloc[:, 8:11].notna().all(axis=1) 
    
    # Combined mask for samples that are BOTH valid AND fixation-end
    combined_mask_original = fixation_mask & valid_samples_mask

    # Get the data columns for ALL rows (no filtering yet)
    numerical_cols = [colNumEnum.TIME.value, colNumEnum.HIT_X.value, colNumEnum.HIT_Y.value, colNumEnum.HIT_Z.value]
    numerical_vals = raycast_df.iloc[:, numerical_cols]
    
    obj_name_col = raycast_df.columns[colNumEnum.OBJ_NAME.value]
    obj_names_series = raycast_df[obj_name_col]

    # Return the full data and the masks for categorization
    return numerical_vals.to_numpy(), obj_names_series.to_numpy(), fixation_mask.to_numpy(), valid_samples_mask.to_numpy()

def read_numerical_vals(csv_path: str, colNumEnum: Enum) -> np.array:
    
    raycast_df = process_types(csv_path) #update samples with correct samples
    fixation_mask = raycast_df.iloc[:, 0].isin(["SAMPLEENDFIX"])
    valid_samples_mask = raycast_df.iloc[:, 8:11].notna().all(axis=1) 
    combined_mask = fixation_mask & valid_samples_mask #remove fixation_mask to include all points
    #combined_mask = valid_samples_mask #this version of combined mask does not account for fixation and non fixations
    #combined_mask = True
    num_values = raycast_df.loc[combined_mask].iloc[:,[colNumEnum.TIME.value,colNumEnum.HIT_X.value,colNumEnum.HIT_Y.value,colNumEnum.HIT_Z.value]]
    return num_values.to_numpy()
    
    '''
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        time_col = colNumEnum.TIME
        return np.array([[float(row[time_col.value]), float(row[colNumEnum.HIT_X.value]),
                          float(row[colNumEnum.HIT_Y.value]), float(row[colNumEnum.HIT_Z.value])]
                         for row in reader if '' not in row[8:11]])
    '''
def read_event_type(csv_path: str, colNumEnum : Enum) -> np.array:
    raycast_df = process_types(csv_path) #update samples with correct samples
    
    #look for fixations
    fixation_mask = raycast_df.iloc[:, 0].isin(["SAMPLEENDFIX"])
    valid_samples_mask = raycast_df.iloc[:, 8:11].notna().all(axis=1)
    combined_mask = fixation_mask & valid_samples_mask #remove fixation_mask to include all points
    #combined_mask = valid_samples_mask 
    #combined_mask = True
    obj_names_series = raycast_df.loc[combined_mask, raycast_df.columns[colNumEnum.OBJ_NAME.value]]
    print(len(obj_names_series))
    return obj_names_series.to_numpy()

    #with open(csv_path, 'r') as file:
        #reader = csv.reader(file)
        #return np.array([row[colNumEnum.OBJ_NAME.value] for row in reader if '' not in row[8:11]])
        #print(len(np.array([row[colNumEnum.OBJ_NAME.value] for row in reader if '' not in row[8:11]])))    
    

def process_types(csv_path):
    """
    Vectorized processing of sample types
    """
    raycast_df = pd.read_csv(csv_path, header=None)
    first_col = raycast_df.iloc[:,0]
    
    start_mask = (first_col == 'SAMPLESTARTFIX')
    end_mask = (first_col == 'SAMPLEENDFIX')

    
    if start_mask.any() and end_mask.any():
        
        first_start_index = start_mask.idxmax()
        first_end_index = end_mask.idxmax()
        if first_end_index < first_start_index:
            end_mask.loc[first_end_index] = False
            
    shifted_end_mask = np.roll(end_mask.astype(int), -1)
    sample_type_mask = (first_col == 'SAMPLE_TYPE')
    region_changes = start_mask.astype(int) - shifted_end_mask.astype(int)
    inside_region = np.cumsum(region_changes) > 0
    inside_mask = sample_type_mask & inside_region
    modified_first_col = first_col.copy()
    modified_first_col[inside_mask] = 'SAMPLE_FIX'
    raycast_df[0] = modified_first_col
    return raycast_df


class colNumsSingleCast(Enum):
    TIME = 1
    OBJ_NAME = 2
    HIT_X = 9
    HIT_Y = 10
    HIT_Z = 11

class colNumsMulticast(Enum):  # Renamed to follow the same convention
    TIME = 1
    OBJ_NAME = 2
    HIT_X = 3
    HIT_Y = 4
    HIT_Z = 5
