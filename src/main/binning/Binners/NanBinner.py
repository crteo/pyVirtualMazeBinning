import numpy as np

from enum import Enum
from . import Binner

DEFAULT_SIZE = (25,25)
DEFAULT_CENTER = (0,0,0)
FLOOR_BIN_SIZE = Binner.GLOB_BIN_DEFAULT_SIZE # axis-specific, & height
class NanBinner(Binner.Binner):
    center = np.array((np.nan,np.nan,np.nan))
    size = np.array(DEFAULT_SIZE)
    bin_cache = np.zeros((0,0,0))
    
    def __init__(self, center = DEFAULT_CENTER, size = DEFAULT_SIZE):
        #ignore all
        self.bin_cache = np.zeros((1,1,1))
    
    
    def add_to_bin(self, point : tuple) -> tuple:
       # Easy case : Will only ever need to consider x & z
       
       # convention : use x as width, z as height
       self.bin_cache[0,0,0] += 1
       return 0,0,0
        
        
    def get_all_binCounts(self):
        return self.bin_cache.ravel(order='C')
        
    


