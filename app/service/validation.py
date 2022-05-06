# Copyright 2018-2022 Institute of Neuroscience and Medicine (INM-1),
# Forschungszentrum Jülich GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import siibra
from fastapi import HTTPException
from siibra.core import Space, Parcellation, Region, Atlas, BoundingBox


def validate_and_return_atlas(atlas_id: str) -> Atlas:
    """
    Check if the given atlas id is valid and return an atlas object
    If the atlas id is not valid, throw a HTTP 400 Exception

    :param atlas_id: id that needs to be checked
    :return: siibra atlas object
    """
    try:
        return siibra.atlases[atlas_id]
    except:
        raise HTTPException(
            status_code=400,
            detail=f"atlas_id: {atlas_id} is not known"
        )


def validate_and_return_space(space_id: str, atlas: Atlas = None) -> Space:
    """
    Check if the given space id is valid and return a space object
    If the space id is not valid, throw a HTTP 400 Exception

    :param space_id: id that needs to be checked
    :param atlas: if atlas is not None, get spaces from the provided atlas instance
    :return: siibra space object
    """
    try:
        if atlas is not None:
            return atlas.spaces[space_id]
        else:
            return siibra.spaces[space_id]
    except:
        raise HTTPException(
            status_code=400,
            detail=f"space_id: {space_id} is not known"
        )


def validate_and_return_parcellation(parcellation_id: str, atlas: Atlas = None) -> Parcellation:
    """
    Check if the given parcellation id is valid and return a parcellation object
    If the parcellation id is not valid, throw a HTTP 400 Exception

    :param parcellation_id: id that needs to be checked
    :param atlas: if atlas is not None, get parcellations from the provided atlas instance
    :return: siibra parcellation object
    """
    try:
        if atlas is not None:
            return atlas.parcellations[parcellation_id]
        else:
            return siibra.parcellations[parcellation_id]
    except:
        raise HTTPException(
            status_code=400,
            detail=f"parcellation_id: {parcellation_id} is not known"
        )


def validate_and_return_region(region_id: str, parcellation: Parcellation) -> Region:
    """
    Check if the given region id is valid and return a region object
    If the region id is not valid, throw a HTTP 400 Exception
    Parcellation.find_regions is used rather than decode_region, as region name 
    can sometimes be ambiguous. find_regions on the other hand, rank the result
    based on closeness score.

    :param region_id: id that needs to be checked
    :param parcellation: parcellation to search the region in
    :return: siibra region object
    """
    try:
        return parcellation.find_regions(region_id)[0]
    except:
        raise HTTPException(
            status_code=404,
            detail=f"region: {region_id} is not known"
        )


def validate_and_return_bbox(bbox: str, space: Space) -> BoundingBox:
    try:
        import json
        boundingbox = json.loads(bbox)
        assert len(boundingbox) == 2, f"expected list with length 2"
        assert all(len(point) == 3 for point in boundingbox), f"expected every element in list to have len 3"
        assert all(isinstance(num, float) or isinstance(num, int) for point in boundingbox for num in point), f"expected every element to be a float"
        return BoundingBox(boundingbox[0], boundingbox[1], space)
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"getting voi bad request: {str(e)}"
        )


file_response_openapi = {
    200: {
        "content": {
            "application/octet-stream": {
                "schema": {
                    "type": "string",
                    "format": "binary"
                }
            }
        }
    }
}
