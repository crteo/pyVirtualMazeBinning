

import pandas as pd
import numpy as np
from . import bin_consts



def apply_binners(binner_arr, point_arr) :
    out_arr = np.zeros((binner_arr.shape[0],3))
    # needs to be 3 as the output of add_to_bin has 3 cols, two for the bin, one for the face
    
    BINNER_LIST = (binner for binner in bin_consts.BINNERS)
    #.value call needed to convert to the actual underlying class
    for binner in BINNER_LIST :
        relevant_points = np.equal(binner_arr,binner)
        out_arr[relevant_points,:] = binner.value.add_to_bin(point_arr[relevant_points,:])
    return out_arr

    
def get_mappers(name_arr : np.array, point_arr : np.array) :

    
    
    name_series = pd.Series(name_arr)
    out_series = pd.Series(np.zeros(name_arr.shape))
    
    def get_mapper(obj_name : str) :
        def isin(A, B):
            for item_a in A:
                if item_a in B.lower():
                    return True
            return False
        if "NaN" in obj_name :
            return bin_consts.BINNERS.NAN_BINNER
        if "BlueWall" in obj_name or isin(["pig","cat","m_wall_29", "m_wall_6", "m_wall_21", "m_wall_10"], obj_name):
            return bin_consts.BINNERS.PILLAR_BLUE_BINNER
        if "GreenWall" in obj_name  or isin(["rabit","m_wall_26", "m_wall_25", "m_wall_1", "m_wall_5"], obj_name)   :
            return bin_consts.BINNERS.PILLAR_GREEN_BINNER
        if "RedWall" in obj_name or isin(["donkey","crocodile","m_wall_4", "m_wall_3", "m_wall_15", "m_wall_24"], obj_name):
            return bin_consts.BINNERS.PILLAR_RED_BINNER
        if "YellowWall" in obj_name  or isin(["camel","m_wall_7", "m_wall_8", "m_wall_12", "m_wall_20"], obj_name):
            return bin_consts.BINNERS.PILLAR_YELLOW_BINNER
        if "Ground" in obj_name :
            return bin_consts.BINNERS.FLOOR_BINNER
        if "ceil" in obj_name.lower() :
            return bin_consts.BINNERS.CEILING_BINNER
        if "WallsPerimeter" in obj_name or "wall" in obj_name.lower() :
            return bin_consts.BINNERS.BOUNDARY_BINNER
        if "CueImage" in obj_name :
            return bin_consts.BINNERS.CUE_BINNER
        if "HintImage" in obj_name :
            return bin_consts.BINNERS.HINT_BINNER
        else :
            print(f"Undefined name {obj_name}, returning NaN Binner")
            raise Exception("Undefined name, exiting") 
    
    out_series = \
        name_series.map(get_mapper)
    
    # now, handle poster indices
    
    out_arr = out_series.to_numpy()

    return out_arr


def find_closest_mazewall(point_arr : np.array) :
    # calc array of distances and do minning

    pillar_centers = np.vstack(tuple(pillar.center for pillar in bin_consts.PILLARS))
    
    pillar_centers = pillar_centers.T.reshape((1,3,-1)) 
    #move all the centers into the 3rd dimension
    #so it looks like [x,y,z] stacked in the 3rd dimension
    #do it this way so we can calculate distances in vectorised form
    
    #first, get the raw array
    
    raw_dists = point_arr.reshape((point_arr.shape) + (1,)) - pillar_centers #broadcasting will ensure this is okay
    
    #then, square
    
    squared_dists = np.square(raw_dists)
    
    #then, sum across the rows, which is axis 1.
    
    summed_dists = np.sum(squared_dists,axis=1)
    
    #skip sqrt because for comparison, it's not needed
    
    min_indexes = np.argmin(summed_dists,axis=1) 
    #across the index which indexes pillar type, which was 2, but is now 1 due to summing collapsing a dim
    
    #1-d index array obtained, then just index!
    
    return np.array(bin_consts.PILLARS)[min_indexes]
