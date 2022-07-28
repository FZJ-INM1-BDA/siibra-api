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
import requests
import re
from os import path
from urllib.parse import quote

import zipfile
import siibra

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from starlette.responses import FileResponse, StreamingResponse

from app.service.request_utils import get_feature_cls_from_name, get_spatial_features, get_voi, split_id, get_file_from_nibabel, get_parcellations_for_space
from app.service.request_utils import get_base_url_from_request, siibra_custom_json_encoder,origin_data_decoder
from app.service.validation import validate_and_return_atlas, validate_and_return_parcellation, validate_and_return_space

from app import logger

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

    threesurfer_volume_spec = [spec for spec in space._dataset_specs if spec.get("volume_type") == "threesurfer/gii"]
    if len(threesurfer_volume_spec) > 0:

        zipbuffer = io.BytesIO()
        with zipfile.ZipFile(zipbuffer, "a", zipfile.ZIP_DEFLATED, False) as zipfilehandle:
            for spec in [spec for spec in threesurfer_volume_spec]:
                surfaces = spec.get('detail', {}).get('threesurfer/gii', {}).get('surfaces', [])
                root_url = spec.get('url')
                for surface in surfaces:
                    surface_url = re.sub(r'^root:', root_url, surface.get('url'))
                    resp = requests.get(surface_url)
                    filename = path.basename(surface_url)
                    zipfilehandle.writestr(filename, resp.content)

        return Response(zipbuffer.getvalue(), headers={
            'content-disposition': f'attachment;filename={space.name}.zip'
        }, media_type="application/x-zip-compressed")
    
    template = atlas.get_template(space).fetch()

    # create file-object in memory
    # file_object = io.BytesIO()
    filename = get_file_from_nibabel(template, 'template', space)

    return FileResponse(filename, filename=filename)

allow_list_parcellation_map = ("nii", "")

@router.get('/{atlas_id:path}/spaces/{space_id:path}/parcellation_maps', tags=['spaces'])
# add parcellations_map_id as optional param
def get_parcellation_map_for_space(atlas_id: str, space_id: str, parcellation_id: Optional[str]=None):
    """
    Returns all parcellation maps for a given space id.
    """
    atlas = validate_and_return_atlas(atlas_id)
    space = validate_and_return_space(space_id, atlas)

    if parcellation_id is not None:
        parcellation = validate_and_return_parcellation(parcellation_id, atlas)
        relevant_maps = [spec for spec in parcellation._dataset_specs
            if spec.get("space_id") is not None
            and siibra.spaces[spec.get("space_id")] is space
            and spec.get("volume_type") in allow_list_parcellation_map]
        
        assert all(map.get("url") is not None for map in relevant_maps), f"all relevant maps' url should be defined"

        if len(relevant_maps) == 0:
            raise HTTPException(404, detail=f"Could not find any volume files for {space_id}, {parcellation_id}")

        zipbuffer = io.BytesIO()
        with zipfile.ZipFile(zipbuffer, "a", zipfile.ZIP_DEFLATED, False) as zipfilehandle:
            for spec in [spec for spec in relevant_maps]:
                resp = requests.get(spec.get("url"))
                filename = path.basename(spec.get("url"))
                zipfilehandle.writestr(filename, resp.content)
        return Response(zipbuffer.getvalue(), headers={
            'content-disposition': f'attachment;filename={space.name}-{parcellation.name}.zip'
        }, media_type="application/x-zip-compressed")

    valid_parcs = [p for p in siibra.parcellations if p.supports_space(space)]

    if len(valid_parcs) == 1:
        maps = [valid_parcs[0].get_map(space)]
        filename = get_file_from_nibabel(maps[0], 'maps', space)
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
                get_file_from_nibabel(
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
        parcellation_id: Optional[str] = None, region: Optional[str] = None, bbox: Optional[str] = None):
    """
    Get more information for a single feature.
    A parcellation id and region id can be provided optional to get more details.
    """
    logger.debug(f'api endpoint: get_single_spatial_feature, {atlas_id}, {space_id}, {modality_id}, {parcellation_id}, {region}')
    if bbox is not None:
        try:
            import json
            list_of_points = json.loads(bbox)
            assert len(list_of_points) == 2, f"expected list with length 2"
            assert all(len(point) == 3 for point in list_of_points), f"expected every element in list to have len 3"
            assert all(isinstance(num, float) or isinstance(num, int) for point in list_of_points for num in point), f"expected every element to be a float"
            return get_voi(atlas_id, space_id, list_of_points)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"getting voi bad request: {str(e)}"
            )
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

    def is_spatial_feature(ft: str):
        try:
            featurecls = get_feature_cls_from_name(ft)
            return issubclass(featurecls[0], siibra.features.features.SpatialFeature)
        except:
            return False
    return {
        'features': [{
            feature.modality(): '{}atlases/{}/spaces/{}/features/{}'.format(
                get_base_url_from_request(request),
                atlas_id.replace('/', '%2F'),
                space_id.replace('/', '%2F'),
                quote(feature.modality())
            ) for feature in siibra.features.modalities if is_spatial_feature(feature)
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
