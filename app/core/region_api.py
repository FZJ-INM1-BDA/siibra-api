from typing import Callable, List, Optional, Tuple

from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse

import siibra
from siibra import atlases, parcellations, spaces
from siibra.core import Region, Atlas, Space, Parcellation

from app.configuration.diskcache import memoize
from app.service.request_utils import get_path_to_regional_map
from app import logger

REGION_PATH = "/regions"

router = APIRouter(prefix=REGION_PATH)


TAGS=["regions"]


def parse_region_param(parse_regionid=False):
    def region_router_decorator(fn: Callable):
        
        def inner(atlas_id:str, parcellation_id: str, space_id: Optional[str], *args, **kwargs):

            try:
                atlas = atlases[atlas_id]
            except Exception:
                return HTTPException(
                    status_code=404,
                    detail=f"atlas with id: {atlas_id} not found."
                )
            
            try:
                parcellation = atlas.parcellations[parcellation_id]
            except Exception:
                return HTTPException(
                    status_code=404,
                    detail=f"parcellation with id: {parcellation_id} not found in atlas {str(atlas)}."
                )

            if space_id is not None:
                try:
                    space = atlas.spaces[space_id]
                except Exception:
                    return HTTPException(
                        status_code=404,
                        detail=f"space with id: {space_id} not found in atlas {str(atlas)}."
                    )
            
            if parse_regionid:
                region_id = kwargs.get("region_id")
                try:
                    region = parcellation.decode_region(region_id)
                except Exception:
                    return HTTPException(
                        status_code=404,
                        detail=f"region with region_id {region_id} cannot be found",
                    )
            return fn(*args, **kwargs, atlas=atlas, parcellation=parcellation, space=space, region=region)
        
        # in principle, should use functools.wraps decorator
        # but it seems doesn't play too well with fastapi/pydantic
        # so... for now, only copying over __doc__ and __name__
        
        inner.__doc__ = fn.__doc__
        inner.__name__ = fn.__name__
        return inner
    return region_router_decorator


@router.get("", tags=TAGS,
            response_model=List[Region.to_model.__annotations__.get("return")])
@parse_region_param()
def get_all_regions_from_atlas_parc_space(atlas: Atlas, parcellation: Parcellation, space: Space):
    """
    Returns all regions for a given parcellation id.
    """
    return [r.to_model(space=space) for r in parcellation.regiontree]


@router.get("/{region_id:path}/features",
            tags=TAGS)
@parse_region_param(parse_regionid=True)
def get_all_features_for_region(
    atlas: Atlas,
    parcellation: Parcellation,
    space: Space,
    region: Region):
    """
    Returns all regional features for a region.
    """
    siibra.get_features(region, modality="all")
    return HTTPException(
        status_code=501,
        detail=f"features has not yet been converted to JSONables"
    )


@router.get("/{region_id:path}/features/{modality}/{feature_id:path}",
            tags=TAGS)
@parse_region_param(parse_regionid=True)
@memoize(typed=True)
def get_regional_modality_by_id(
    atlas: Atlas,
    parcellation: Parcellation,
    space: Space,
    region: Region,
    modality: str,
    feature_id: str,
    gene: Optional[str] = None):
    """
    Returns a feature for a region, as defined by by the modality and feature ID
    """
    siibra.get_features(region, modality="all")
    return HTTPException(
        status_code=501,
        detail=f"feature has not yet been converted to JSONables"
    )


# TODO - can maybe be removed
# negative: need to be able to fetch region specific feature. XG
@router.get("/{region_id:path}/features/{modality}",
            tags=TAGS)
@parse_region_param(parse_regionid=True)
@memoize(typed=True)
def get_feature_modality_for_region(
    atlas: Atlas,
    parcellation: Parcellation,
    space: Space,
    region: Region,
    modality: str,
    gene: Optional[str] = None):
    """
    Returns list of the features for a region, as defined by the modality.
    """
    siibra.get_features(region, modality="modality")

    return HTTPException(
        status_code=501,
        detail=f"feature has not yet been converted to JSONables"
    )


@router.get("/{region_id:path}/regional_map/info",
            tags=TAGS)
@parse_region_param(parse_regionid=True)
@memoize(typed=True)
def get_regional_map_info(
    atlas: Atlas,
    parcellation: Parcellation,
    space: Space,
    region: Region):
    """
    Returns information about a regional map for given region name.
    """
    query_id = f"{atlas.id}{parcellation.id}{region.id}{space.id}"
    logger.debug(f'queryId: {query_id}')
    cached_fullpath = get_path_to_regional_map(query_id, region, space)
    logger.debug(f'cached path: {cached_fullpath}')

    import nibabel as nib
    import numpy as np
    
    nii = nib.load(cached_fullpath)
    data = nii.get_fdata()
    return {
        'min': np.min(data),
        'max': np.max(data),
    }


@router.get("/{region_id:path}/regional_map/map",
            tags=TAGS)
@parse_region_param(parse_regionid=True)
def get_regional_map_file(
    atlas: Atlas,
    parcellation: Parcellation,
    space: Space,
    region: Region):
    """
    Returns a regional map for given region name.
    """
    query_id = f"{atlas.id}{parcellation.id}{region.id}{space.id}"
    logger.debug(f'queryId: {query_id}')
    cached_fullpath = get_path_to_regional_map(query_id, region, space)
    logger.debug(f'cached path: {cached_fullpath}')
    return FileResponse(cached_fullpath, media_type='application/octet-stream')


@router.get("/{region_id:path}",
            tags=TAGS,
            response_model=Region.to_model.__annotations__.get("return"))
@parse_region_param(parse_regionid=True)
def get_single_region_detail(atlas: Atlas, parcellation: Parcellation, space: Space, region: Region):
    return region.to_model(space=space)