from typing import Tuple, Union, List
from pathlib import Path
import json
import time
import os

from new_api.common import get_filename
from .data import extra_data

def cache_region_statistic_map(parcellation_id: str, region_id: str, space_id: str, name: str= "", *, no_cache=False) -> Tuple[str, bool, str]:
    """Retrieve and save regional statistical map (if necessary), and then return the path of the map.

    Args:
        parcellation_id: lookup id of the parcellation of the map
        region_id: lookup id of the region of the map
        space_id: lookup id of the space of the map
    
    Returns:
        path to statistical map, if a cached file is returned, warning text, if any
    """
    import siibra
    import nibabel as nib
    import numpy as np
    import requests

    full_filename = get_filename("statistical_map", parcellation_id, region_id, space_id, ext=".nii.gz")
    warning_texts_arr: List[str] = []
    if not no_cache and os.path.isfile(full_filename):
        try:
            warning_texts_arr.append(Path(f"{full_filename}.warning.txt").read_text())
        except:
            ...
        return full_filename, True, "\n".join(warning_texts_arr) if len(warning_texts_arr) > 0 else None
    if (space_id, parcellation_id) in extra_data:
        extra_cont_map = extra_data[space_id, parcellation_id]
        try:
            volume_idx = extra_cont_map["indices"][region_id][0]["volume"]
            nii_url = extra_cont_map["volumes"][volume_idx]["providers"]["nii"]
            resp = requests.get(nii_url)
            resp.raise_for_status()
            with open(full_filename, "wb") as fp:
                fp.write(resp.content)
            return full_filename, False, None
        except (KeyError, IndexError) as e:
            raise Exception(f"{region_id} cannot be properly parsed") from e
        
    error_text = f"Map with parc id '{parcellation_id}', space id '{space_id}'"

    maps = siibra.find_maps(parcellation_id, space_id, "statistical", name)
    assert len(maps) > 0, f"{error_text} returns None"
    
    if len(maps) > 1:
        warning_texts_arr.append(f"Multiple ({len(maps)}) maps found")
    map = maps[0]
    volume_data = map.fetch(region=region_id)

    error_text = f"{error_text}, with region_id '{region_id}'"
    assert isinstance(volume_data, nib.Nifti1Image), f"{error_text}, volume provided is not of type Nifti1Image"

    if volume_data.get_data_dtype() == np.float64:
        warning_texts_arr.append("datatype is float64. casting to float32")
        data = volume_data.get_fdata()
        data = data.astype(np.float32)
        volume_data = nib.Nifti1Image(data, volume_data.affine, volume_data.header)
    
    nib.save(volume_data, full_filename)

    if len(warning_texts_arr) > 0:
        with open(f"{full_filename}.warning.txt", "w") as fp:
            fp.write("\n".join(warning_texts_arr))

    with open(f"{full_filename}.{str(int(time.time()))}.json", "w") as fp:
        json.dump({
            "prefix": "statistical_map",
            "parcellation_id": parcellation_id,
            "region_id": region_id,
            "space_id": space_id,
        }, fp=fp, indent="\t")
    return full_filename, False, "\n".join(warning_texts_arr) if len(warning_texts_arr) > 0 else None


def cache_parcellation_labelled_map(parcellation_id: str, space_id: str, region_id:Union[str, None]=None, *,  no_cache=False) -> Tuple[str, bool, str]:
    """Retrieve and save labelled map / regional mask (if necessary), and then return the path of the map.

    Args:
        parcellation_id: lookup id of the parcellation of the map
        region_id: lookup id of the region of the map
        space_id: lookup id of the space of the map
    
    Returns:
        path to labelled map/regional mask, if a cached file is returned, warning text, if any
    """
    full_filename = get_filename("labelled_map", parcellation_id, space_id, region_id if region_id else "", ext=".nii.gz")
    if not no_cache and os.path.isfile(full_filename):
        return full_filename, True, None

    import siibra
    import nibabel as nib
    error_text = f"Map with parc id '{parcellation_id}', space id '{space_id}'"

    labelled_map = siibra.get_map(parcellation_id, space_id, "labelled")
    assert labelled_map is not None, f"{error_text} returns None"
    volume_data = None
    if region_id is not None:
        volprov = labelled_map.extract_regional_map(region_id)
    else:
        volprov = labelled_map.extract_full_map()
    volume_data = volprov.get_data()

    assert isinstance(volume_data, nib.Nifti1Image), f"{error_text}, volume provided is not of type Nifti1Image"
    
    nib.save(volume_data, full_filename)
    with open(f"{full_filename}.{str(int(time.time()))}.json", "w") as fp:
        json.dump({
            "prefix": "labelled_map",
            "parcellation_id": parcellation_id,
            "space_id": space_id,
            "region_id": region_id,
        }, fp=fp, indent="\t")
    return full_filename, False, None


def cache_resampled_map(parcellation_id: str, space_id: str, *, no_cache: bool=False):
    full_filename = get_filename("resampled_map", parcellation_id, space_id, ext=".nii.gz")
    if not no_cache and os.path.isfile(full_filename):
        return full_filename, True, None

    import nibabel as nib
    import siibra
    from siibra.operations.volume_fetcher.nifti import ResampleNifti

    mp = siibra.get_map(parcellation_id, space_id, "labelled")
    src_dp = mp.extract_full_map()
    nii = src_dp.get_data()
    space = siibra.get_space(space_id)
    target_dp = space.get_dataprovider(index=0)
    tmpl_nii = target_dp.get_data()
    resampled = ResampleNifti.resample_img_to_img(nii, tmpl_nii)
    
    nib.save(resampled, full_filename)
    with open(f"{full_filename}.{str(int(time.time()))}.json", "w") as fp:
        json.dump({
            "prefix": "resampled_map",
            "parcellation_id": parcellation_id,
            "space_id": space_id,
        }, fp=fp, indent="\t")
    return full_filename, False, None
