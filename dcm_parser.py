from logging import root
from tabnanny import verbose
import pandas as pd
import numpy as np
import pydicom
import os
from pydicom.tag import Tag
from collections import defaultdict
from monai.data import ITKReader
import json

def get_path(root_dir):
    ret_path = list()
    for f in os.listdir(root_dir):
        tmp_path = os.path.join(root_dir, f)
        if os.path.isdir(tmp_path):
            ret_path.extend(get_path(tmp_path))
        else:
            ret_path.append(tmp_path)
    return ret_path
        
def dictify(ds):
    output = dict()
    for elem in ds:
        if elem.VR != 'SQ': 
            output[elem.tag] = elem.value
        else:
            output[elem.tag] = [dictify(item) for item in elem]
    return output



## define some constant here
root_dir = "../siim-original/dicom-images-train"
convert_to_string = True
verbose = False
path = get_path(root_dir)
print(f"number files detected: {len(path)}")


## parse the dicom files
df = defaultdict(lambda : [])
valid_files = []
cruptted_files = []
missing_metadata_files = defaultdict(lambda : [])
for p in path:
    ## check if is a valid dicom files
    try:
        dcm = pydicom.dcmread(p)
        valid_files.append(p)
    except:
        cruptted_files.append(p)
        if verbose:
            print(f"file {p} is missing dicom file meta information header")
        else:
            pass
        
    tmp_json = json.loads(dcm.to_json())
    for k, v in tmp_json.items():
        ## conver to the png files (wait to be done)
        if Tag("PixelData") == k:
            if verbose:
                print("pass the pixel value")
            continue


        ## two options: 1) convert to human readable string format, 2) read directly from tag
        if convert_to_string:
            entry = pydicom.datadict.get_entry(k)
            representation, multiplicity, name, is_retired, keyword = entry
            try:
                df[keyword].append(v['Value'][0])
            except:
                df[keyword].append(None)
                missing_metadata_files[keyword].append(p)
                if verbose:
                    print(f"tag {k} ({keyword}) has no value") 
                else:
                     pass
        else:
            try:
                df[k].append(v['Value'][0])
            except:
                df[k].append(None)
                missing_metadata_files[k].append(p)
                if verbose:
                    print(f"tag {k} has no value") 
                else:
                     pass


df = pd.DataFrame(df)

# train.columns = columns_list
print(df.columns)
df.to_csv("meta.csv")


# Serializing json
json_object = json.dumps(missing_metadata_files, indent=4)
 
# Writing to sample.json
with open("missing.json", "w") as outfile:
    outfile.write(json_object)

