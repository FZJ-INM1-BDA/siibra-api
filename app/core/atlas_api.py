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

from typing import List
import siibra
from fastapi import APIRouter, HTTPException
from fastapi_versioning import version

from siibra.core.json_encoder import JSONEncoder
from siibra.core import Atlas

# FastApi router to create rest endpoints
router = APIRouter(
    prefix='/atlases'
)

from .parcellation_api import router as parcellation_router
from .space_api import router as space_router

router.include_router(space_router, prefix="/{atlas_id:path}")
router.include_router(parcellation_router, prefix="/{atlas_id:path}")

# region === atlases
@router.get('',
            tags=['atlases'],
            response_model=List[Atlas.SiibraSerializationSchema])
@version(1)
def get_all_atlases():
    """
    # Get all atlases

    Get all atlases known by siibra.

    ## code sample

    ```python
    import siibra

    atlases = [atlas for atlas in siibra.atlases]
    ```
    """
    return [JSONEncoder.encode(atlas, nested=True) for atlas in siibra.atlases]


@router.get('/{atlas_id:path}',
            tags=['atlases'],
            response_model=Atlas.SiibraSerializationSchema)
@version(1)
def get_atlas_by_id(atlas_id: str):
    """
    # Get a specific atlas

    Get more information for a specific atlas with links to further objects.

    ## code sample

    ```python
    import siibra

    atlas = siibra.atlases[f'{atlas_id}']
    ```
    """

    try:
        return JSONEncoder.encode(siibra.atlases[atlas_id], nested=True)
    except IndexError:
        raise HTTPException(
            status_code=404,
            detail='atlas with id: {} not found'.format(atlas_id))
