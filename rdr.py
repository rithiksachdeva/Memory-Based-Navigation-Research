import cv2
import numpy as np
import h5py
import time

filename = '1658622612.6630862.hdf5'
with h5py.File(filename, "r") as f:
    # Print all root level object names (aka keys) 
    # these can be group or dataset names 
    print("Keys: %s" % f.keys())
    # get first object name/key; may or may NOT be a group
    for a_group_key in list(f.keys()):

        # get the object type for a_group_key: usually group or dataset
        #print(type(f[a_group_key])) 

        # If a_group_key is a group name, 
        # this gets the object names in the group and returns as a list
        #data = list(f[a_group_key])
        #print(data)

        # preferred methods to get dataset values:
        ds_obj = f[a_group_key]      # returns as a h5py dataset object
        print(type(ds_obj))
        ds_dset = ds_obj.get('Camera')
        for key, val in ds_dset.attrs.items():
            print("    %s: %s" % (key, val))
        data_arr_all = ds_dset[:]
        print(type(data_arr_all))
        print("writing data contents to file")
        cv2.imwrite(str(time.time())+".jpg", data_arr_all)
