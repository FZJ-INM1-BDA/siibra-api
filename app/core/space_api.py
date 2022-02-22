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
from typing import List, Optional, Union

import zipfile
import siibra
from siibra.core import Space
from siibra.features.feature import SpatialFeature
from siibra.features import FeatureQuery, modalities
from siibra.features.ieeg import IEEGSessionModel
from siibra.volumes.volume import VolumeModel
from siibra.core.serializable_concept import JSONSerializable

from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse, StreamingResponse

from app.service.validation import (
    validate_and_return_parcellation,
    validate_and_return_region,
    file_response_openapi,
    FeatureIdNameModel,
)
from app.service.request_utils import  get_voi, get_file_from_nibabel
from app.service.validation import validate_and_return_atlas, validate_and_return_space

SPACE_PREFIX = "/spaces"
TAGS = ["spaces"]

router = APIRouter(prefix=SPACE_PREFIX)

UnionSpatialFeatureModels = Union[
    IEEGSessionModel,
    VolumeModel,
]


@router.get("",
    tags=TAGS,
    response_model=List[Space.to_model.__annotations__.get("return")])
def get_all_spaces(atlas_id: str):
    """
    Returns all spaces that are defined in the siibra client.
    """
    atlas = validate_and_return_atlas(atlas_id)
    return [space.to_model() for space in atlas.spaces]


@router.get("/{space_id:path}/templates",
    tags=TAGS,
    responses=file_response_openapi)
def get_template_by_space_id(atlas_id: str, space_id: str):
    """
    Returns a template for a given space id.
    """
    atlas = validate_and_return_atlas(atlas_id)
    space = validate_and_return_space(space_id)
    template = atlas.get_template(space).fetch()

    # create file-object in memory
    # file_object = io.BytesIO()
    filename = get_file_from_nibabel(template, "template", space)

    return FileResponse(filename, filename=filename, media_type='application/octet-stream')


@router.get("/{space_id:path}/parcellation_maps",
    tags=TAGS,
    responses=file_response_openapi)
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
        filename = get_file_from_nibabel(maps[0], 'maps', space)
        return FileResponse(filename, filename=filename, media_type='application/octet-stream')
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


@router.get("/{space_id:path}/features/{modality_id}/{feature_id}",
    tags=TAGS,
    response_model=UnionSpatialFeatureModels)
def get_single_spatial_feature_detail(
    modality_id: str,
    feature_id: str,
    atlas_id: str,
    space_id: str,
    parcellation_id: Optional[str],
    region: Optional[str]):
    """
    Get a detailed view on a single spatial feature.
    A parcellation id and region id can be provided optional to get more details.
    """

    atlas = validate_and_return_atlas(atlas_id)
    space = validate_and_return_space(space_id, atlas)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas) if parcellation_id else None
    roi = validate_and_return_region(region, parcellation) if parcellation else None
    features: List[UnionSpatialFeatureModels] = siibra.get_features(roi or parcellation or space, modality_id)

    try:
        found_features = [feature for feature in features if feature.id == feature_id]
        return found_features[0].to_model(detail=True)
    except IndexError:
        return HTTPException(
            status_code=404,
            defailt=f"feature with id {feature_id} not found."
        )


@router.get("/{space_id:path}/features/{modality_id}",
    tags=TAGS,
    response_model=List[UnionSpatialFeatureModels])
def get_single_spatial_feature(
        atlas_id: str, space_id: str, modality_id: str,
        parcellation_id: Optional[str] = None, region: Optional[str] = None, bbox: Optional[str] = None):
    """
    Get more information for a single feature.
    A parcellation id and region id can be provided optional to get more details.
    """
    atlas = validate_and_return_atlas(atlas_id)
    space = validate_and_return_space(space_id, atlas)
    if bbox is not None:
        try:
            import json
            list_of_points = json.loads(bbox)
            assert len(list_of_points) == 2, f"expected list with length 2"
            assert all(len(point) == 3 for point in list_of_points), f"expected every element in list to have len 3"
            assert all(isinstance(num, float) or isinstance(num, int) for point in list_of_points for num in point), f"expected every element to be a float"
            return get_voi(space, list_of_points)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"getting voi bad request: {str(e)}"
            )

    parcellation = validate_and_return_parcellation(parcellation_id, atlas) if parcellation_id else None
    roi = validate_and_return_region(region, parcellation) if parcellation else None
    features: List[UnionSpatialFeatureModels] = siibra.get_features(roi or parcellation or space, modality_id)

    return [feature.to_model(detail=False) for feature in features]


@router.get("/{space_id:path}/features",
    tags=TAGS,
    response_model=List[FeatureIdNameModel])
def get_spatial_feature_names(atlas_id: str, space_id: str):
    """
    Return all possible feature names and links to get more details
    """

    return_list = []
    for modality, query_list in [(modality, FeatureQuery._implementations[modality]) for modality in modalities]:
        if all(issubclass(query._FEATURETYPE, SpatialFeature) for query in query_list):
            implemented_flag = all(issubclass(query._FEATURETYPE, JSONSerializable) for query in query_list)
            return_list.append({
                "@id": modality,
                "name": modality,
                "nyi": not implemented_flag,
            })

    return return_list


@router.get("/{space_id:path}/volumes",
    tags=TAGS,
    response_model=List[VolumeModel])
def get_one_space_volumes(atlas_id: str, space_id: str):
    atlas = validate_and_return_atlas(atlas_id)
    space = validate_and_return_space(space_id, atlas)
    return [vol.to_model() for vol in space.volumes]


@router.get("/{space_id:path}",
    tags=TAGS,
    response_model=Space.to_model.__annotations__.get("return"))
def get_one_space_by_id(atlas_id: str, space_id: str):
    """
    Returns one space for given id, with links to further resources
    """
    atlas = validate_and_return_atlas(atlas_id)
    return validate_and_return_space(space_id, atlas).to_model()

