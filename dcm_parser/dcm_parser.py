import pandas as pd
import numpy as np
import pydicom
import os
from pydicom.tag import Tag
from collections import defaultdict

from skimage import io
import skvideo.io
import json
import warnings

from joblib import parallel_backend
from joblib import Parallel, delayed
from tqdm import tqdm
import operator
from functools import reduce

def get_path(root_dir: str) -> list:
    """recursivly acquire path to the dicom file

    Args:
        root_dir (str): dirtory that contains the dicom file

    Returns:
        list: list of path to the dicom files
    """
    ret_path = list()
    for f in os.listdir(root_dir):
        tmp_path = os.path.join(root_dir, f)
        if os.path.isdir(tmp_path):
            ret_path.extend(get_path(tmp_path))
        else:
            ret_path.append(tmp_path)
    return ret_path
        

def dcm_to_png(dcm: pydicom.dataset.FileDataset, path:str)->None:
    """convert dicom to png and save to file

    Args:
        dcm (pydicom.dataset.FileDataset): target dicom
        path (str): saved path
    """
    img = dcm.pixel_array.astype(float)
    img = ((img - np.amin(img))/np.amax(img)) * 255
    img = np.uint8(img)
    if len(img.shape) > 2:
        img = np.expand_dims(img, axis=0)
        vid = np.transpose(img, (1, 2, 3, 0))
        skvideo.io.vwrite(path, vid)
    else:
        io.imsave(path, img)


def get_meta(p:str, convert_to_string:bool=True, verbose:bool=False, save_img:bool=False, img_dest_folder:str="./png/")->dict:
    """extract metadata of dicom filefrom path

    Args:
        p (str): path to the dicom file
        convert_to_string (bool, optional): convert all meta data to string. Defaults to True.
        verbose (bool, optional): print out logs. Defaults to False.
        save_img (bool, optional): save png(2D)/mp4(3D) files. Defaults to False.
        img_dest_folder (str, optional): path to the saved dir. Defaults to "./png/".

    Returns:
        dict: _description_
    """
    os.makedirs(img_dest_folder, exist_ok=True)
    ret_dict = {}
    metadata, missing_metadata_files = defaultdict(lambda: {}), defaultdict(lambda: [])
    corrupted_files, valid_files = [], []
    metadata['path'] = p

    try:
        dcm = pydicom.dcmread(p)
        valid_files.append(p)
        metadata['file_shape'] = dcm.pixel_array.shape
    except:
        corrupted_files.append(p)
        if verbose:
            print(f"file {p} is missing dicom file meta information header")
        ret_dict.update({
            'metadata': metadata,
            'corrupted_files': corrupted_files,
            'valid_files': valid_files,
            'missing_metadata_file': missing_metadata_files
        })
        return ret_dict
    
    if save_img:
        fname = p.split("\\")[-1].split("/")[-1]
        if len(dcm.pixel_array.shape) == 2:
            save_file = f"{img_dest_folder}/{fname}.png"
        else:
            save_file = f"{img_dest_folder}/{fname}.mp4"
        dcm_to_png(dcm, save_file)
    
    tmp_json = json.loads(dcm.to_json())
    for k, v in tmp_json.items():
        if Tag("PixelData") == k:
            if verbose:
                print("pass the pixel value")
            continue
        
        if convert_to_string:
            try:
                entry = pydicom.datadict.get_entry(k)
                representation, multiplicity, name, is_retired, keyword = entry
                metadata[keyword] = v['Value'][0]
            except:
                metadata[keyword] = None
                missing_metadata_files[keyword].append(p)
                if verbose:
                    print(f"tag {k} ({keyword}) has no value")
                else:
                    pass
        else:
            try:
                metadata[k] = v['Value'][0]
            except:
                metadata[k] = None
                missing_metadata_files[k].append(p)
                if verbose:
                    print(f"tag {k} has no value")
                else:
                    pass

    ret_dict.update({
        'metadata': metadata,
        'corrupted_files': corrupted_files,
        'valid_files': valid_files,
        'missing_metadata_file': missing_metadata_files
    })
    return ret_dict


def batch_extraction(source_dir:str, dest_dir:str, save_img = True):
    """extract meta data from dicom in batch

    Args:
        source_dir (str): source directory that contains dicom files
        dest_dir (str): target directory of where the output file will be saved
        save_img (bool, optional): save pixels arrays to png/mp4. Defaults to True.

    Returns:
        meta_df (DataFrame): dataframe object that stores the dicom meta data
        corrupted_files (list): a list of corrupted files that cannot be exectute normally
        valid files (list): a list of valid files that processed normally
        missing_metadata_files (list): a list of files that complete/partial missing meta data
    """
    path = get_path(source_dir)
    print(f"number files detected: {len(path)}")

    valid_files, corrupted_files = [], []
    missing_metadata_files, df = defaultdict(lambda: []), defaultdict(lambda: defaultdict(lambda: []))

    with parallel_backend('threading', n_jobs=-1):
        tmp_dict = Parallel()(delayed(get_meta)(p, verbose=False, save_img=save_img, img_dest_folder=f"{dest_dir}/") for p in tqdm(path))
    
    # unpack files from dict
    meta_df = [tmp_dict[i]['metadata'] for i in range(len(tmp_dict))]
    corrupted_files = [tmp_dict[i]['corrupted_files'] for i in range(len(tmp_dict))]
    corrupted_files = reduce(operator.iconcat, corrupted_files, [])
    valid_files = [tmp_dict[i]['valid_files'] for i in range(len(tmp_dict))]
    valid_files = reduce(operator.iconcat, valid_files, [])
    missing_metadata_files = [tmp_dict[i]['missing_metadata_file'] for i in range(len(tmp_dict))]
    
    meta_df = pd.DataFrame(meta_df)
    meta_df.set_index('path')
    return meta_df, corrupted_files, valid_files, missing_metadata_files

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="convert dicom to video/png")
    parser.add_argument("--source", type=str, help="where to load the dicom file")
    parser.add_argument("--dest", type=str, help="where to save the png/mp4 file")
    parser.add_argument("--thread", type=int, default=20, help="where to save the png/mp4 file")
    args = parser.parse_args()

    warnings.filterwarnings("ignore", category=FutureWarning)    
    pydicom.config.convert_wrong_length_to_UN = True
    dest_dir = args.dest
    source_dir = args.source
    
    meta_df, corrupted_files, valid_files, missing_metadata_files = batch_extraction(source_dir=source_dir, dest_dir=dest_dir)

    # save output files
    meta_df.to_csv(f"{dest_dir}/meta.csv")
    json_object = json.dumps(missing_metadata_files, indent=4)

    with open(f"{dest_dir}/missing.json", "w") as outfile:
        outfile.write(json_object)

    meta_df = pd.DataFrame({"path": corrupted_files})
    meta_df.to_csv(f"{dest_dir}/corrupted_files.csv")
    
