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

from fastapi import APIRouter, HTTPException
from fastapi_versioning import version

from app.core.parcellation_api import router as parcellation_router
from app.core.space_api import router as space_router

from siibra.core import Atlas
from siibra import atlases


ATLAS_PATH = "/atlases"
router = APIRouter(prefix=ATLAS_PATH)

router.include_router(parcellation_router, prefix="/{atlas_id:path}")
router.include_router(space_router, prefix="/{atlas_id:path}")


@router.get('', tags=['atlases'], response_model=List[Atlas.to_model.__annotations__.get("return")])
@version(1)
def get_all_atlases():
    """
    Get all atlases known by siibra.
    """
    return [atlas.to_model() for atlas in atlases]


@router.get('/{atlas_id:path}', tags=['atlases'], response_model=Atlas.to_model.__annotations__.get("return"))
@version(1)
def get_atlas_by_id(atlas_id: str):
    """
    Get more information for a specific atlas with links to further objects.
    """
    try:
        atlas = atlases[atlas_id]
        return atlas.to_model().dict()
    except:
        return HTTPException(
            status_code=404,
            detail=f"atlas with id: {atlas_id} not found."
        )
