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
from siibra.core import Space, Atlas
from siibra.features.ieeg import IEEGSessionModel
from siibra.features.voi import VOIDataModel
from siibra.volumes.volume import VolumeModel

from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse, StreamingResponse

from app.service.validation import (
    validate_and_return_bbox,
    validate_and_return_parcellation,
    validate_and_return_region,
    file_response_openapi,
)

from app.models import RestfulModel
from app.service.request_utils import  get_all_serializable_spatial_features, get_file_from_nibabel
from app.service.validation import validate_and_return_atlas, validate_and_return_space

SPACE_PREFIX = "/spaces"
TAGS = ["spaces"]

router = APIRouter(prefix=SPACE_PREFIX)

UnionSpatialFeatureModels = Union[
    IEEGSessionModel,
    VOIDataModel,
]


class SapiSpaceModel(Space.to_model.__annotations__.get("return"), RestfulModel):
    @staticmethod
    def from_space(space: Space) -> 'SapiSpaceModel':

        model = space.to_model()
        assert len(space.atlases) == 1, f"Expecting only 1 set of atlases associated with space {space}"
        atlas: Atlas = list(space.atlases)[0]
        atlas_id = atlas.to_model().id

        return SapiSpaceModel(
            **model.dict(),
            links=SapiSpaceModel.create_links(atlas_id=atlas_id, space_id=model.id)
        )


@router.get("",
    tags=TAGS,
    response_model=List[SapiSpaceModel])
def get_all_spaces(atlas_id: str):
    """
    Returns all spaces that are defined in the siibra client.
    """
    atlas = validate_and_return_atlas(atlas_id)
    return [SapiSpaceModel.from_space(space) for space in atlas.spaces]


@router.get("/{space_id:lazy_path}/templates",
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


@router.get("/{space_id:lazy_path}/parcellation_maps",
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


@router.get("/{space_id:lazy_path}/features/{feature_id}",
    tags=TAGS,
    response_model=UnionSpatialFeatureModels)
def get_single_detailed_spatial_feature(
    feature_id: str,
    atlas_id: str,
    space_id: str,
    parcellation_id: Optional[str]=None,
    region: Optional[str]=None,
    bbox: Optional[str]=None):
    """
    Get a detailed view on a single spatial feature.
    A parcellation id and region id can be provided optional to get more details.
    """

    atlas = validate_and_return_atlas(atlas_id)
    space = validate_and_return_space(space_id, atlas)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas) if parcellation_id else None
    region = validate_and_return_region(region, parcellation) if region and parcellation else None

    boundingbox = validate_and_return_bbox(bbox, space) if bbox else None

    try:
        features = get_all_serializable_spatial_features(space=space, parcellation=parcellation, region=region, bbox=boundingbox)
        found_features = [feature for feature in features if feature.model_id == feature_id]
        return found_features[0].to_model(detail=True, roi=region or parcellation, bbox=boundingbox)
    except IndexError:
        return HTTPException(
            status_code=404,
            detail=f"feature with id {feature_id} not found."
        )

@router.get("/{space_id:lazy_path}/features",
    tags=TAGS,
    response_model=List[UnionSpatialFeatureModels])
@SapiSpaceModel.decorate_link("features")
def get_all_spatial_features_for_space(
    atlas_id: str,
    space_id: str,
    parcellation_id: Optional[str]=None,
    region: Optional[str]=None,
    bbox: Optional[str]=None):
    """
    Return all possible feature names and links to get more details
    """

    atlas = validate_and_return_atlas(atlas_id)
    space = validate_and_return_space(space_id, atlas)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas) if parcellation_id else None
    region = validate_and_return_region(region, parcellation) if region and parcellation else None

    boundingbox = validate_and_return_bbox(bbox, space) if bbox else None

    features = get_all_serializable_spatial_features(space=space, parcellation=parcellation, region=region, bbox=boundingbox)
    return [feat.to_model(detail=False) for feat in features]


@router.get("/{space_id:lazy_path}/volumes",
    tags=TAGS,
    response_model=List[VolumeModel])
@SapiSpaceModel.decorate_link("volumes")
def get_volumes_for_space(atlas_id: str, space_id: str):
    atlas = validate_and_return_atlas(atlas_id)
    space = validate_and_return_space(space_id, atlas)
    return [vol.to_model() for vol in space.volumes]


@router.get("/{space_id:lazy_path}",
    tags=TAGS,
    response_model=SapiSpaceModel)
@SapiSpaceModel.decorate_link("self")
def get_single_space_detail(atlas_id: str, space_id: str):
    """
    Returns one space for given id, with links to further resources
    """
    atlas = validate_and_return_atlas(atlas_id)
    space = validate_and_return_space(space_id, atlas)
    return SapiSpaceModel.from_space(space)

