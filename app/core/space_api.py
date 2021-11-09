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

from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel
from siibra.core.jsonable import SiibraSerializable
from siibra.features.voi import VolumeOfInterest
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

import siibra
from siibra.core import Atlas, Space, Parcellation, Region
from siibra.core.json_encoder import JSONEncoder
from siibra.features.feature import SpatialFeature
from siibra.features.ieeg import IEEG_Session

from app.service.request_utils import get_cached_file_path
from app.service.validation import file_response_openapi

# FastApi router to create rest endpoints
router = APIRouter(
    prefix='/spaces'
)



SpatialFeatureEnum: Enum = Enum('SpatialFeatureEnum', {
    mod.modality(): f'{mod.modality()}{" (Coming soon)" if not issubclass(mod._FEATURETYPE, SiibraSerializable) else ""}' for mod in siibra.features.modalities
        if issubclass(mod._FEATURETYPE, SpatialFeature)
})


@router.get('',
            tags=['spaces'],
            response_model=List[Space.SiibraSerializationSchema])
def get_all_spaces(atlas_id: str):
    """
    # Get all space specified by the atlas

    Returns all spaces supported by the atlas specified by the atlas_id.

    ## code sample

    ```python
    import siibra

    atlas = siibra.atlases[f'{atlas_id}']
    spaces = atlas.spaces
    ```
    """
    try:
        atlas: Atlas=siibra.atlases[atlas_id]
        return [ JSONEncoder.encode(space, nested=True) for space in atlas.spaces]
    except IndexError:
        raise HTTPException(404, detail=f'atlas with id {atlas_id} not found.')


@router.get('/{space_id:path}/templates',
            tags=['spaces'],
            responses=file_response_openapi)
def get_template_by_space_id(
        atlas_id: str,
        space_id: str):
    """
    # Get the image volume of the reference template

    Get the image volume of the reference template as a NiFTi .nii.gz file.

    ## code sample
    ```python
    from siibra.core import Atlas, Space
    import siibra
    import nibabel as nib

    atlas: Atlas = siibra.atlases[f'{atlas_id}']
    space: Space = atlas.spaces[f'{space_id}']
    nii = space.get_template()
    nib.save(nii, 'template.nii.gz')
    ```
    """
    try:
        atlas: Atlas = siibra.atlases[atlas_id]
        space: Space = atlas.spaces[space_id]
        filename = f'space-tmpl-image-{hash(atlas_id + space_id)}.nii.gz'
        def get_nii_and_save(full_path):
            import nibabel as nib
            nii = space.get_template()
            nib.save(nii, full_path)
        cached_full_path = get_cached_file_path(filename, get_nii_and_save)
        return cached_full_path

    except IndexError as e:
        raise HTTPException(404, detail=f'IndexError: {str(e)}')
    except RuntimeError as e:
        # siibra-python raises sometimes
        raise HTTPException(500, detail=f'RuntimeError: {str(e)}')
    except Exception as e:
        raise HTTPException(500, detail=f'Exception: {str(e)}')


@router.get('/{space_id:path}/parcellation_maps',
            tags=['spaces'],
            responses=file_response_openapi)
# add parcellations_map_id as optional param
def get_parcellation_map_for_space(atlas_id: str, space_id: str):
    """
    # Returns all parcellation maps of an atlas in a given space

    Returns all parcellation maps of an atlas in a given space, in nii.gz format.

    ## code sample

    ```python
    import siibra
    from siibra.core import Atlas, Parcellation, Space

    atlas: Atlas = siibra.atlases[f'{atlas_id}']
    space: Space = atlas.spaces[f'{space_id}']
    filtered_parcs: List[Parcellation] = [p for p in atlas.parcellations if p.supports_space(space)]
    
    maps = [p.get_map(space) for p in filtered_parcs]
    ```
    """

    try:
        atlas: Atlas = siibra.atlases[f'{atlas_id}']
        space: Space = atlas.spaces[f'{space_id}']
        filtered_parcs: List[Parcellation] = [p for p in atlas.parcellations if p.supports_space(space)]
        
        if len(filtered_parcs) > 1:
            raise HTTPException(501, detail=f'Retriving multiple parcellation maps not yet implemented')
        
        parc = filtered_parcs[0]
        map = parc.get_map(space)

        cached_filename = '{}-{}.nii.gz'.format('map', space.name.replace(' ', '_'))
        def callback(full_path: str):
            import nibabel as nib
            nib.save(map, full_path)
        full_path =  get_cached_file_path(cached_filename, callback)
        return FileResponse(full_path, media_type='application/octet-stream')
    except IndexError as e:
        raise HTTPException(404, detail=f'IndexError: {str(e)}')

    # TODO get all parc maps, NYI
    # maps = [p.get_map(space) for p in valid_parcs]
    # files = []
    # mem_zip = io.BytesIO()

    # label_index = 0
    # for map in maps:
    #     files.append(
    #         get_file_from_nibabel(
    #             map,
    #             'map-{}'.format(label_index),
    #             space))
    #     label_index = label_index + 1

    # with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
    #     for f in files:
    #         zf.write(f)
    #         print(zf.namelist())

    # mem_zip.seek(0)
    # response = StreamingResponse(
    #     iter([mem_zip.getvalue()]), media_type="application/x-zip-compressed")
    # response.headers["Content-Disposition"] = 'attachment; filename=maps-{}.zip'.format(
    #     space.name.replace(' ', '_'))
    # return response



SpatialFeatureSchemas = Union[
    IEEG_Session.SiibraSerializationSchema,
    VolumeOfInterest.SiibraSerializationSchema,
]


@router.get('/{space_id:path}/features/{modality_id}',
            tags=['spaces', 'features'],
            response_model=List[SpatialFeatureSchemas])
def get_single_spatial_feature(
    atlas_id: str,
    space_id: str,
    modality_id: SpatialFeatureEnum,
    parcellation_id: Optional[str] = None,
    region_id: Optional[str] = None):
    """
    # Get all spatial features of a specific type

    Returns a list of spatial features of the specified type.
    If parcellation_id and region_id are provided, the item in the list will contain a 'in_roi' bool field.

    ## code sample
    ```python
    from siibra.core import Atlas, Space, Parcellation, Region

    atlas:Atlas = siibra.atlases[f'{atlas_id}']
    space:Space = atlas.spaces[f'{space_id}']

    if f'{parcellation_id}' or f'{region_id}':
        parcellation:Parcellation = atlas.parcellations['f{parcellation_id}'] if 'f{parcellation_id}' else None
        region:Region = parcellation.find_regions(f'{region_id}')[0] if parcellation_id else atlas.get_region(f'{region_id}')
        roi = region or parcellation
        features = [f for f in siibra.get_features(roi, modality_id) if f.space == space]
    else:
        queries = siibra.features.FeatureQuery.queries(modality_id)
        assert len(queries) == 1, f'modality_id query should be unique, but got {len(queries)} responses'
        query = queries[0]
        features = [f for f in query.features if f.space == space]
    ```
    """
    try:
        modality_id = modality_id.name
        atlas:Atlas = siibra.atlases[atlas_id]
        space:Space = atlas.spaces[space_id]

        if parcellation_id or region_id:
            parcellation:Parcellation = atlas.parcellations[parcellation_id] if parcellation_id else None
            region:Region = parcellation.find_regions(region_id)[0] if parcellation_id else atlas.get_region(region_id) if region_id else None
            roi = region or parcellation
            features = [f for f in siibra.get_features(roi, modality_id) if f.space == space]
        else:
            queries = siibra.features.FeatureQuery.queries(modality_id)
            assert len(queries) == 1, f'modality_id query should be unique, but got {len(queries)} responses'
            query = queries[0]
            features = [f for f in query.features if f.space == space]
        return JSONEncoder.encode(features, nested=True, detail=False)

    except IndexError as e:
        raise HTTPException(404, detail=f'IndexError: {str(e)}')
    except AssertionError as e:
        raise HTTPException(400, detail=f'AssertionError: {str(e)}')



@router.get('/{space_id:path}/features/{modality_id}/{feature_id}',
            tags=['spaces', 'features'],
            response_model=SpatialFeatureSchemas)
def get_single_spatial_feature_detail(
        atlas_id: str,
        space_id: str,
        modality_id: SpatialFeatureEnum,
        feature_id: str,
        parcellation_id: Optional[str] = None,
        region_id: Optional[str] = None):
    """
    # Get a spatial features specified by the feature_id 

    Returns a specific spatial feature specified by feature_id.
    If parcellation_id and region_id are provided, the item in the list will contain a 'in_roi' bool field.

    ## code sample
    ```python
    from siibra.core import Atlas, Space, Parcellation, Region

    atlas:Atlas = siibra.atlases[f'{atlas_id}']
    space:Space = atlas.spaces[f'{space_id}']

    if f'{parcellation_id}' or f'{region_id}':
        parcellation:Parcellation = atlas.parcellations['f{parcellation_id}'] if 'f{parcellation_id}' else None
        region:Region = parcellation.find_regions(f'{region_id}')[0] if parcellation_id else atlas.get_region(f'{region_id}')
        roi = region or parcellation
        features = [f for f in siibra.get_features(roi, modality_id) if f.space == space]
    else:
        queries = siibra.features.FeatureQuery.queries(modality_id)
        assert len(queries) == 1, f'modality_id query should be unique, but got {len(queries)} responses'
        query = queries[0]
        features = [f for f in query.features if f.space == space]
    feature, = [f for f in features if f.id == feature_id]
    ```
    """
    try:
        modality_id = modality_id.name
        atlas:Atlas = siibra.atlases[atlas_id]
        space:Space = atlas.spaces[space_id]
        roi = None
        if parcellation_id or region_id:
            parcellation:Parcellation = atlas.parcellations[parcellation_id] if parcellation_id else None
            region:Region = parcellation.find_regions(region_id)[0] if parcellation_id else atlas.get_region(region_id)
            roi = region or parcellation
            features = [f for f in siibra.get_features(roi, modality_id) if f.space == space]
        else:
            queries = siibra.features.FeatureQuery.queries(modality_id)
            assert len(queries) == 1, f'modality_id query should be unique, but got {len(queries)} responses'
            query = queries[0]
            features = [f for f in query.features if f.space == space]
        feature = [f for f in features if (f.dataset.id if hasattr(f, 'dataset') else f.id) == feature_id][0]
        return JSONEncoder.encode(feature, region=roi, nested=True, detail=True)

    except IndexError as e:
        raise HTTPException(404, detail=f'IndexError: {str(e)}')
    except AssertionError as e:
        raise HTTPException(400, detail=f'AssertionError: {str(e)}')


class NamedModel(BaseModel):
    name: SpatialFeatureEnum


@router.get('/{space_id:path}/features',
            tags=['spaces', 'features'],
            response_model=List[NamedModel])
def get_spatial_feature_names(
    atlas_id: str,
    space_id: str):
    """
    # Get all types of spatial features

    Returns all available types of spatial features.

    ## code sample

    ```python
    import siibra
    from siibra.features.feature import SpatialFeature

    parcellation_feature_types = [mod for mod in siibra.features.modalities if issubclass(mod._FEATURETYPE, SpatialFeature) ]
    ```
    """
    
    try:
        # only required for validation
        _atlas:Atlas = siibra.atlases[atlas_id]
        _space:Space = _atlas.spaces[space_id]
        return [{
            'name': mod.value
        } for mod in SpatialFeatureEnum ]
    except IndexError as e:
        raise HTTPException(404, detail=f'IndexError: {str(e)}')


@router.get('/{space_id:path}',
            tags=['spaces'],
            response_model=Space.SiibraSerializationSchema)
def get_one_space_by_id(
        atlas_id: str,
        space_id: str):
    """
    # Get a specific reference space

    Returns the reference space specified by space_id, restricted by atlas selected by atlas_id

    ## code sample

    ```python
    import siibra

    atlas = siibra.atlases[f'{atlas_id}']
    space = atlas.spaces[f'{space_id}']
    ```
    """
    try:
        atlas:Atlas = siibra.atlases[atlas_id]
        space:Space = atlas.spaces[space_id]
        return JSONEncoder.encode(space, nested=True)
    except IndexError:
        raise HTTPException(
            status_code=404,
            detail='atlas with id: {} and/or space with {} not found'.format(atlas_id, space_id))
