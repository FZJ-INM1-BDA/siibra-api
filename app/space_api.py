# Copyright 2018-2020 Institute of Neuroscience and Medicine (INM-1), Forschungszentrum Jülich GmbH

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

from .atlas_api import ATLAS_PATH

# FastApi router to create rest endpoints
router = APIRouter()


# region === spaces


@router.get(ATLAS_PATH + '/{atlas_id:path}/spaces')
def get_all_spaces(atlas_id: str, request: Request):
    """
    Parameters:
        - atlas_id

    Returns all spaces that are defined in the brainscapes client.
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
                        request.base_url,
                        atlas_id.replace('/', '%2F'),
                        space.id.replace('/', '%2F')
                    )
                }
            }
        })
    return jsonable_encoder(result)





@router.get(ATLAS_PATH+'/{atlas_id:path}/spaces/{space_id:path}/templates')
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


@router.get(ATLAS_PATH+'/{atlas_id:path}/spaces/{space_id:path}/parcellation_maps')
def get_parcellation_map_for_space(atlas_id: str, space_id: str):  # add parcellations_map_id as optional param
    """
    Parameters:
        - atlas_id
        - space_id

    Returns all maps for a given space id.
    """
    atlas = create_atlas(atlas_id)
    space = find_space_by_id(atlas, space_id)
    maps = atlas.get_maps(space)
    print(maps.keys())

    if len(maps) == 1:
        filename = _get_file_from_nibabel(maps[0], 'maps', space)
        return FileResponse(filename, filename=filename)
    else:
        files = []
        mem_zip = io.BytesIO()

        for label, space_map in maps.items():
            files.append(_get_file_from_nibabel(space_map, label, space))

        with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.write(f)
                print(zf.namelist())

        mem_zip.seek(0)
        response = StreamingResponse(iter([mem_zip.getvalue()]), media_type="application/x-zip-compressed")
        response.headers["Content-Disposition"] = 'attachment; filename=maps-{}.zip'.format(space.name.replace(' ', '_'))
        return response
    raise HTTPException(status_code=404, detail='Maps for space with id: {} not found'.format(space_id))


@router.get(ATLAS_PATH+'/{atlas_id:path}/spaces/{space_id:path}')
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
        json_result = jsonable_encoder(space)
        json_result['availableParcellations'] = get_parcellations_for_space(space.name)
        json_result['links'] = {
            'regions': {
                'href': '{}atlases/{}/spaces/{}/regions'.format(
                    request.base_url,
                    atlas_id.replace('/', '%2F'),
                    space.id.replace('/', '%2F')
                )
            },
            'templates': {
                'href': '{}atlases/{}/spaces/{}/templates'.format(
                    request.base_url,
                    atlas_id.replace('/', '%2F'),
                    space.id.replace('/', '%2F')
                )
            },
            'parcellation_maps': {
                'href': '{}atlases/{}/spaces/{}/parcellation_maps'.format(
                    request.base_url,
                    atlas_id.replace('/', '%2F'),
                    space.id.replace('/', '%2F')
                )
            }
        }
        return json_result
    else:
        raise HTTPException(status_code=404, detail='space with id: {} not found'.format(space_id))


# endregion
