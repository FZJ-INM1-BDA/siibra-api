# Copyright 2018-2020 Institute of Neuroscience and Medicine (INM-1),
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
from enum import Enum
from typing import List, Optional
from fastapi import APIRouter, Request, HTTPException
from siibra.core.datasets import EbrainsDataset
from siibra.core.parcellation import Parcellation
from siibra import atlases
from starlette.responses import FileResponse
from fastapi.encoders import jsonable_encoder
from app.service.request_utils import get_base_url_from_request
from app.service.request_utils import get_global_features
from app.service.validation import validate_and_return_atlas, validate_and_return_parcellation, \
    validate_and_return_space, validate_and_return_region
from app import logger
from app.core.region_api import router as region_router

preheat_flag = False


PARCELLATION_PATH = "/parcellations"


router = APIRouter(prefix=PARCELLATION_PATH)
router.include_router(region_router, prefix="/{parcellation_id:path}")


@router.get("", tags=['parcellations'], response_model=List[Parcellation.to_model.__annotations__.get("return")])
def get_all_parcellations(atlas_id: str):
    """
    Returns all parcellations that are defined in the siibra client for given atlas.
    """
    try:
        atlas = atlases[atlas_id]
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"atlas with id: {atlas_id} not found."
        )
    
    return [p.to_model() for p in atlas.parcellations]


def parse_region_selection(
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        space_id: str):
    if space_id is None:
        raise HTTPException(
            status_code=400,
            detail='space_id is required for this functionality')

    space_of_interest = validate_and_return_space(space_id)
    validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id)
    region = validate_and_return_region(region_id, parcellation)
    if region is None:
        raise HTTPException(
            status_code=404,
            detail=f'cannot find region with spec {region_id}')
    # if len(region) > 1:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f'found multiple region withs pec {region_id}')
    return region, space_of_interest


@router.get('/{parcellation_id:path}/features/{modality}/{modality_instance_name}',
            tags=['parcellations'])
def get_single_global_feature_detail(
        atlas_id: str,
        parcellation_id: str,
        modality: str,
        modality_instance_name: str,
        request: Request):
    """
    Returns a global feature for a specific modality id.
    """
    try:
        fs = get_global_features(atlas_id, parcellation_id, modality)
        found = [f for f in fs if f['src_name'] == modality_instance_name]
        if len(found) == 0:
            raise HTTPException(
                status_code=404,
                detail=f'modality with name {modality_instance_name} not found')

        return {
            'result': found[0]
        }
    except NotImplementedError:
        raise HTTPException(status_code=501,
                             detail=f'modality {modality} not yet implemented')


@router.get('/{parcellation_id:path}/features/{modality}',
            tags=['parcellations'])
def get_single_global_feature(
        atlas_id: str,
        parcellation_id: str,
        modality: str,
        request: Request):
    """
    Returns a global feature for a parcellation, filtered by given modality.
    """
    try:
        fs = get_global_features(atlas_id, parcellation_id, modality)
        return fs
    except NotImplementedError:
        raise HTTPException(status_code=501,
                             detail=f'modality {modality} not yet implemented')


@router.get('/{parcellation_id:path}/features',
            tags=['parcellations'])
def get_global_features_rest(
        atlas_id: str,
        parcellation_id: str,
        request: Request):
    """
    Returns all global features for a parcellation.
    """
    validate_and_return_atlas(atlas_id)
    validate_and_return_parcellation(parcellation_id)
    result = {
        'features': [
            {
                m: '{}atlases/{}/parcellations/{}/features/{}'.format(
                    get_base_url_from_request(request),
                    atlas_id.replace(
                        '/',
                        '%2F'),
                    parcellation_id.replace(
                        '/',
                        '%2F'),
                    m
                )} for m in siibra.features.modalities  # TODO siibra.get_features(parcellation, 'all') - too slow at the moment
        ]}

    return jsonable_encoder(result)


@router.get('/{parcellation_id:path}',
            tags=['parcellations'],
            response_model=Parcellation.to_model.__annotations__.get("return"))
def get_parcellation_by_id(
        atlas_id: str,
        parcellation_id: str):
    """
    Returns one parcellation for given id.
    """
    try:
        atlas = atlases[atlas_id]
        parcellation = atlas.parcellations[parcellation_id]
        return parcellation.to_model().dict()
    except IndexError as e:
        raise HTTPException(
            status_code=404,
            detail=f"atlas_id {atlas_id} parcellation_id {parcellation_id} not found. {str(e)}"
        )
