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

import zipfile

from fastapi import APIRouter, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from starlette.responses import FileResponse, StreamingResponse

from .request_utils import create_atlas, split_id, find_space_by_id, _get_file_from_nibabel, get_parcellations_for_space
from .request_utils import get_base_url_from_request, siibra_custom_json_encoder
from .atlas_api import ATLAS_PATH
import siibra as sb

# FastApi router to create rest endpoints
router = APIRouter()


# region === spaces


@router.get(ATLAS_PATH + '/{atlas_id:path}/spaces')
def get_all_spaces(atlas_id: str, request: Request):
    """
    Parameters:
        - atlas_id

    Returns all spaces that are defined in the siibra client.
    """
    atlas = create_atlas(atlas_id)
    atlas_spaces = atlas.spaces
    result = []
    for space in atlas_spaces:
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


@router.get(ATLAS_PATH + '/{atlas_id:path}/spaces/{space_id:path}/templates')
def get_template_by_space_id(atlas_id: str, space_id: str):
    """
    Parameters:
        - atlas_id
        - space_id

    Returns all templates for a given space id.
    """
    atlas = create_atlas(atlas_id)
    space = find_space_by_id(atlas, space_id)
    template = atlas.get_template(space)

    # create file-object in memory
    # file_object = io.BytesIO()
    filename = _get_file_from_nibabel(template, 'template', space)

    return FileResponse(filename, filename=filename)


@router.get(ATLAS_PATH +
            '/{atlas_id:path}/spaces/{space_id:path}/parcellation_maps')
# add parcellations_map_id as optional param
def get_parcellation_map_for_space(atlas_id: str, space_id: str):
    """
    Parameters:
        - atlas_id
        - space_id

    Returns all maps for a given space id.
    """
    atlas = create_atlas(atlas_id)
    space = find_space_by_id(atlas, space_id)
    valid_parcs = [p for p in sb.parcellations if p.supports_space(space)]

    if len(valid_parcs) == 1:
        maps = [valid_parcs[0].get_map(space)]
        filename = _get_file_from_nibabel(maps[0], 'maps', space)
        return FileResponse(filename, filename=filename)
    else:
        raise HTTPException(
            status=501,
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


@router.get(ATLAS_PATH + '/{atlas_id:path}/spaces/{space_id:path}')
def get_one_space_by_id(atlas_id: str, space_id: str, request: Request):
    """
    Parameters:
        - atlas_id
        - space_id

    Returns space for given id.
    """
    atlas = create_atlas(atlas_id)
    space = find_space_by_id(atlas, space_id)
    if space:
        json_result = jsonable_encoder(
            space, custom_encoder=siibra_custom_json_encoder)
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
            }
        }
        return json_result
    else:
        raise HTTPException(
            status_code=404,
            detail='space with id: {} not found'.format(space_id))

# endregion
