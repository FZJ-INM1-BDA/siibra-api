from typing import Tuple, Union
from pathlib import Path
import json
import time
import os

from new_api.common import get_filename

def cache_region_statistic_map(parcellation_id: str, region_id: str, space_id: str, extra_spec: str= "", *, no_cache=False) -> Tuple[str, bool, str]:
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

    full_filename = get_filename("statistical_map", parcellation_id, region_id, space_id, ext=".nii.gz")
    warning_texts = None
    if not no_cache and os.path.isfile(full_filename):
        try:
            warning_texts = Path(f"{full_filename}.warning.txt").read_text()
        except:
            ...
        return full_filename, True, warning_texts

    error_text = f"Map with parc id '{parcellation_id}', space id '{space_id}'"

    maps = siibra.find_maps(parcellation_id, space_id, "statistical", extra_spec)
    assert len(maps) > 0, f"{error_text} returns None"
    
    if len(maps) > 1:
        warning_texts = f"Multiple ({len(maps)}) maps found"

    volume_data = maps[0].fetch(region=region_id)

    error_text = f"{error_text}, with region_id '{region_id}'"
    assert isinstance(volume_data, nib.Nifti1Image), f"{error_text}, volume provided is not of type Nifti1Image"
    
    nib.save(volume_data, full_filename)

    if warning_texts:
        with open(f"{full_filename}.warning.txt", "w") as fp:
            fp.write(warning_texts)

    with open(f"{full_filename}.{str(int(time.time()))}.json", "w") as fp:
        json.dump({
            "prefix": "statistical_map",
            "parcellation_id": parcellation_id,
            "region_id": region_id,
            "space_id": space_id,
        }, fp=fp, indent="\t")
    return full_filename, False, warning_texts


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

    volume_data = None
    if region_id is not None:
        region = siibra.get_region(parcellation_id, region_id)
        volume_data = region.fetch_regional_map(space_id, "labelled")
    else:
        labelled_map = siibra.get_map(parcellation_id, space_id, "labelled")
        assert labelled_map is not None, f"{error_text} returns None"
        volume_data = labelled_map.fetch()

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


def cache_resampled_map(parcellation_id: str, space_id: str, *, no_cache: bool):
    full_filename = get_filename("resampled_map", parcellation_id, space_id, ext=".nii.gz")
    if not no_cache and os.path.isfile(full_filename):
        return full_filename, True, None

    import nibabel as nib
    import siibra
    from siibra.commons.maps import resample_img_to_img

    mp = siibra.get_map(parcellation_id, space_id, "labelled")
    nii = mp.fetch()
    space = siibra.get_space(space_id)
    tmpl_nii = space.fetch_template()
    resampled = resample_img_to_img(nii, tmpl_nii)
    
    nib.save(resampled, full_filename)
    with open(f"{full_filename}.{str(int(time.time()))}.json", "w") as fp:
        json.dump({
            "prefix": "resampled_map",
            "parcellation_id": parcellation_id,
            "space_id": space_id,
        }, fp=fp, indent="\t")
    return full_filename, False, None
