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

import io
from typing import Optional
from urllib.parse import quote

import zipfile
import siibra

from fastapi import APIRouter, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from starlette.responses import FileResponse, StreamingResponse

from app.service.request_utils import get_spatial_features, split_id, _get_file_from_nibabel, get_parcellations_for_space
from app.service.request_utils import get_base_url_from_request, siibra_custom_json_encoder,origin_data_decoder
from app.service.validation import validate_and_return_atlas, validate_and_return_space

# FastApi router to create rest endpoints
router = APIRouter()


# region === spaces


@router.get('/{atlas_id:path}/spaces', tags=['spaces'])
def get_all_spaces(atlas_id: str, request: Request):
    """
    Returns all spaces that are defined in the siibra client.
    """
    atlas = validate_and_return_atlas(atlas_id)
    result = []
    for space in atlas.spaces:
        result.append({
            'id': split_id(space.id),
            'name': space.name,
            'links': {
                'self': {
                    'href': '{}atlases/{}/spaces/{}'.format(
                        get_base_url_from_request(request),
                        atlas_id.replace('/', '%2F'),
                        space.id.replace('/', '%2F')
                    )
                }
            }
        })
    return jsonable_encoder(result)


@router.get('/{atlas_id:path}/spaces/{space_id:path}/templates', tags=['spaces'])
def get_template_by_space_id(atlas_id: str, space_id: str):
    """
    Returns a template for a given space id.
    """
    atlas = validate_and_return_atlas(atlas_id)
    space = validate_and_return_space(space_id)
    template = atlas.get_template(space).fetch()

    # create file-object in memory
    # file_object = io.BytesIO()
    filename = _get_file_from_nibabel(template, 'template', space)

    return FileResponse(filename, filename=filename)


@router.get('/{atlas_id:path}/spaces/{space_id:path}/parcellation_maps', tags=['spaces'])
# add parcellations_map_id as optional param
def get_parcellation_map_for_space(atlas_id: str, space_id: str):
    """
    Returns all parcellation maps for a given space id.
    """
    validate_and_return_atlas(atlas_id)
    space = validate_and_return_space(space_id)
    valid_parcs = [p for p in siibra.parcellations if p.supports_space(space)]

    if len(valid_parcs) == 1:
        maps = [valid_parcs[0].get_map(space)]
        filename = _get_file_from_nibabel(maps[0], 'maps', space)
        return FileResponse(filename, filename=filename)
    else:
        raise HTTPException(
            status_code=501,
            detail=f'space with id {space_id} has multiple parc, not yet implemented')
        maps = [p.get_map(space) for p in valid_parcs]
        files = []
        mem_zip = io.BytesIO()

        label_index = 0
        for map in maps:
            files.append(
                _get_file_from_nibabel(
                    map,
                    'map-{}'.format(label_index),
                    space))
            label_index = label_index + 1

        with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.write(f)
                print(zf.namelist())

        mem_zip.seek(0)
        response = StreamingResponse(
            iter([mem_zip.getvalue()]), media_type="application/x-zip-compressed")
        response.headers["Content-Disposition"] = 'attachment; filename=maps-{}.zip'.format(
            space.name.replace(' ', '_'))
        return response
    raise HTTPException(
        status_code=404,
        detail='Maps for space with id: {} not found'.format(space_id))


@router.get('/{atlas_id:path}/spaces/{space_id:path}/features/{modality_id}', tags=['spaces'])
def get_single_spatial_feature(
        atlas_id: str, space_id: str, modality_id: str, request: Request,
        parcellation_id: Optional[str] = None, region: Optional[str] = None):
    """
    Get more information for a single feature.
    A parcellation id and region id can be provided optional to get more details.
    """
    got_features = get_spatial_features(atlas_id, space_id, modality_id, parc_id=parcellation_id, region_id=region)
    return got_features


@router.get('/{atlas_id:path}/spaces/{space_id:path}/features/{modality_id}/{feature_id}', tags=['spaces'])
def get_single_spatial_feature_detail(
        atlas_id: str, space_id: str, modality_id: str, feature_id: str, request: Request,
        parcellation_id: Optional[str] = None, region: Optional[str] = None):
    """
    Get a detailed view on a single spatial feature.
    A parcellation id and region id can be provided optional to get more details.
    """
    got_features = get_spatial_features(atlas_id, space_id, modality_id, feature_id, parc_id=parcellation_id, region_id=region, detail=True)
    if len(got_features) == 0:
        raise HTTPException(404, detail=f'feature with id {feature_id} cannot be found')
    return got_features[0]


@router.get('/{atlas_id:path}/spaces/{space_id:path}/features', tags=['spaces'])
def get_spatial_feature_names(atlas_id: str, space_id: str, request: Request):
    """
    Return all possible feature names and links to get more details
    """
    validate_and_return_atlas(atlas_id)
    space = validate_and_return_space(space_id)
    # TODO: Getting all features with result takes to much time at the moment
    # features = siibra.get_features(space, 'all')

    return {
        'features': [{
            feature.modality(): '{}atlases/{}/spaces/{}/features/{}'.format(
                get_base_url_from_request(request),
                atlas_id.replace('/', '%2F'),
                space_id.replace('/', '%2F'),
                quote(feature.modality())
            ) for feature in siibra.features.modalities if issubclass(feature._FEATURETYPE, siibra.features.feature.SpatialFeature)
        }]
    }


@router.get('/{atlas_id:path}/spaces/{space_id:path}', tags=['spaces'])
def get_one_space_by_id(atlas_id: str, space_id: str, request: Request):
    """
    Returns one space for given id, with links to further resources
    """
    validate_and_return_atlas(atlas_id)
    space = validate_and_return_space(space_id)
    if space:
        json_result = jsonable_encoder(
            space, custom_encoder=siibra_custom_json_encoder)
        # TODO: Error on first call
        json_result['availableParcellations'] = get_parcellations_for_space(
            space)
        json_result['links'] = {
            'templates': {
                'href': '{}atlases/{}/spaces/{}/templates'.format(
                    get_base_url_from_request(request),
                    atlas_id.replace('/', '%2F'),
                    space.id.replace('/', '%2F')
                )
            },
            'parcellation_maps': {
                'href': '{}atlases/{}/spaces/{}/parcellation_maps'.format(
                    get_base_url_from_request(request),
                    atlas_id.replace('/', '%2F'),
                    space.id.replace('/', '%2F')
                )
            },
            'features': {
                'href': '{}atlases/{}/spaces/{}/features'.format(
                    get_base_url_from_request(request),
                    atlas_id.replace('/', '%2F'),
                    space.id.replace('/', '%2F')
                )
            }
        }
        if hasattr(space, 'origin_datainfos'):
            json_result['originDatainfos'] = [ origin_data_decoder(datainfo) for datainfo in space.origin_datainfos]
        return json_result
    else:
        raise HTTPException(
            status_code=404,
            detail='space with id: {} not found'.format(space_id))

# endregion
