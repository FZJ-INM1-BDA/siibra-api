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
from starlette.requests import Request

from app.core.parcellation_api import router as parcellation_router
from app.core.space_api import router as space_router
from app.service.validation import (
    validate_and_return_atlas,
)
from app.models import RestfulModel, HrefModel

from siibra.core import Atlas
from siibra import atlases


ATLAS_PATH = "/atlases"
router = APIRouter(prefix=ATLAS_PATH)

router.include_router(parcellation_router, prefix="/{atlas_id:path}")
router.include_router(space_router, prefix="/{atlas_id:path}")

class SapiAtlasModel(Atlas.to_model.__annotations__.get("return"), RestfulModel):
    @staticmethod
    def from_atlas(atlas: Atlas, curr_path: str) -> 'SapiAtlasModel':
        model = atlas.to_model()
        return SapiAtlasModel(
            **model.dict(),
            links={
                "spaces": {
                    "href": f"/{curr_path}/{model.id}/spaces"
                },
                "parcellations": {
                    "href": f"/{curr_path}/{model.id}/parcellations"
                },
            }
        )

@router.get('', tags=['atlases'], response_model=List[SapiAtlasModel])
@version(1)
def get_all_atlases(request: Request):
    """
    Get all atlases known by siibra.
    """
    return [SapiAtlasModel.from_atlas(atlas, request.url.path) for atlas in atlases]


@router.get('/{atlas_id:path}', tags=['atlases'], response_model=SapiAtlasModel)
@version(1)
def get_atlas_by_id(atlas_id: str, request: Request):
    """
    Get more information for a specific atlas with links to further objects.
    """
    atlas = validate_and_return_atlas(atlas_id)
    return SapiAtlasModel.from_atlas(atlas, request.url.path)
