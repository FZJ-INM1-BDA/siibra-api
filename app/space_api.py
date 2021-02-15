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

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.responses import FileResponse, StreamingResponse

import request_utils

from brainscapes.features import regionprops
from atlas_api import ATLAS_PATH

# FastApi router to create rest endpoints
router = APIRouter()


# region === spaces


@router.get(ATLAS_PATH + '/{atlas_id:path}/spaces')
def get_all_spaces(atlas_id: str):
    """
    Parameters:
        - atlas_id

    Returns all spaces that are defined in the brainscapes client.
    """
    atlas = request_utils.create_atlas(atlas_id)
    atlas_spaces = atlas.spaces
    result = []
    for space in atlas_spaces:
        result.append({
            "id": request_utils.split_id(space.id),
            "name": space.name
        })
    return jsonable_encoder(result)


@router.get(ATLAS_PATH+'/{atlas_id:path}/spaces/{space_id:path}/regions')
def get_all_regions_for_space_id(atlas_id: str, space_id: str):
    """
    Parameters:
        - atlas_id
        - space_id

    Returns all regions for a given space id.
    """
    atlas = request_utils.create_atlas(atlas_id)
    # select atlas parcellation
    # Throw Bad Request error or 404 if bad space id
    result = []
    for region in atlas.regiontree.children:
        region_json = request_utils.create_region_json_object(region)
        request_utils._add_children_to_region(region_json, region)
        result.append(region_json)
    return result


@router.get(ATLAS_PATH+'/{atlas_id:path}/spaces/{space_id:path}/regions/{region_id}')
def get_region_by_name(atlas_id: str, space_id: str, region_id):
    """
    Parameters:
        - atlas_id
        - space_id
        - region_id

    Returns all regions for a given space id.
    """
    atlas = request_utils.create_atlas(atlas_id)
    region = atlas.regiontree.find(region_id)
    # select atlas parcellation
    # Throw Bad Request error or 404 if bad space id

    r = region[0]
    region_json = request_utils.create_region_json_object(r)
    request_utils._add_children_to_region(region_json, r)
    atlas.select_region(r)
    r_props = regionprops.RegionProps(atlas, request_utils.find_space_by_id(atlas, space_id))
    region_json['props'] = {}
    region_json['props']['centroid_mm'] = list(r_props.attrs['centroid_mm'])
    region_json['props']['volume_mm'] = r_props.attrs['volume_mm']
    region_json['props']['surface_mm'] = r_props.attrs['surface_mm']
    region_json['props']['is_cortical'] = r_props.attrs['is_cortical']

    return jsonable_encoder(region_json)


@router.get(ATLAS_PATH+'/{atlas_id:path}/spaces/{space_id:path}/templates')
def get_template_by_space_id(atlas_id: str, space_id: str):
    """
    Parameters:
        - atlas_id
        - space_id

    Returns all templates for a given space id.
    """
    atlas = request_utils.create_atlas(atlas_id)
    space = request_utils.find_space_by_id(atlas, space_id)
    template = atlas.get_template(space)

    # create file-object in memory
    # file_object = io.BytesIO()
    filename = request_utils._get_file_from_nibabel(template, 'template', space)

    return FileResponse(filename, filename=filename)


@router.get(ATLAS_PATH+'/{atlas_id:path}/spaces/{space_id:path}/parcellation_maps')
def get_parcellation_map_for_space(atlas_id: str, space_id: str):  # add parcellations_map_id as optional param
    """
    Parameters:
        - atlas_id
        - space_id

    Returns all maps for a given space id.
    """
    atlas = request_utils.create_atlas(atlas_id)
    space = request_utils.find_space_by_id(atlas, space_id)
    maps = atlas.get_maps(space)
    print(maps.keys())

    if len(maps) == 1:
        filename = request_utils._get_file_from_nibabel(maps[0], 'maps', space)
        return FileResponse(filename, filename=filename)
    else:
        files = []
        mem_zip = io.BytesIO()

        for label, space_map in maps.items():
            files.append(request_utils._get_file_from_nibabel(space_map, label, space))

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
def get_one_space_by_id(atlas_id: str, space_id: str):
    """
    Parameters:
        - atlas_id
        - space_id

    Returns space for given id.
    """
    atlas = request_utils.create_atlas(atlas_id)
    space = request_utils.find_space_by_id(atlas, space_id)
    if space:
        return jsonable_encoder(space)
    else:
        raise HTTPException(status_code=404, detail='space with id: {} not found'.format(space_id))


# endregion
