from typing import Literal
from pathlib import Path

from new_api.common.decorators import data_decorator
from new_api.siibra_api_config import ROLE
from new_api.common import get_filename
from new_api.v3.serialization import instance_to_model
from .data import extra_data

def cache_region_statistic_map(parcellation_id: str, region_id: str, space_id: str, name: str= "", *, no_cache=False) -> tuple[str, bool, str]:
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

    fname, cache = siibra.statistical_map_nii_gz(parcellation_id, region_id, space_id)

    if not no_cache:
        return fname, cache, None
    
    Path(fname).unlink()
    fname, cache = siibra.statistical_map_nii_gz(parcellation_id, region_id, space_id)
    return fname, cache, None


@data_decorator(ROLE)
def assign(parcellation_id: str, space_id: str, point: str, assignment_type: str=Literal["statistical", "labelled"], sigma_mm: float=0., extra_specs: str=""):
    import siibra
    df = siibra.assign(point, parcellation_id, space_id, assignment_type)
    return instance_to_model(df, detail=True).dict()
    

@data_decorator(ROLE)
def statistical_map_nii_gz(parcellation_id: str, region_id: str, space_id: str, extra_spec: str="", *, no_cache: bool=False):
    filename, return_cached, warningtext = cache_region_statistic_map(parcellation_id, region_id, space_id, extra_spec, no_cache=no_cache)
    return filename, return_cached

@data_decorator(ROLE)
def statistical_map_info_json(parcellation_id: str, region_id: str, space_id: str, extra_spec: str="", *, no_cache: bool=False):
    filename, return_cached, warningtext = cache_region_statistic_map(parcellation_id, region_id, space_id, extra_spec, no_cache=no_cache)

    import nibabel as nib
    import numpy as np
    nii = nib.load(filename)
    data = nii.get_fdata()
    return {
        "min": np.min(data),
        "max": np.max(data),
    }
