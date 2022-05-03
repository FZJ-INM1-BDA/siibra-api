# Copyright 2018-2022 Institute of Neuroscience and Medicine (INM-1),
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

from typing import Callable, List, Optional, Tuple, Union
from fastapi import APIRouter, HTTPException
from siibra.features import FeatureQuery
from app.core.region_api import UnionRegionalFeatureModels


FEATURE_PATH = "/features"

router = APIRouter(prefix=FEATURE_PATH)

TAGS = ["features"]


@router.get("/{feature_id:lazy_path}", tags=TAGS,
            response_model=UnionRegionalFeatureModels)
def get_feature_details(feature_id: str,
                        atlas_id: Optional[str] = None,
                        space_id: Optional[str] = None,
                        parcellation_id: Optional[str] = None,
                        region_id: Optional[str] = None):
    """
    Get all details for one feature by id.
    Since the feature id is unique, no atlas concept is required.

    Further optional params can extend the result.
    :param feature_id:
    :param atlas_id:
    :param space_id:
    :param parcellation_id:
    :param region_id:
    :return: UnionRegionalFeatureModels
    """
    feature = FeatureQuery.get_feature_by_id(feature_id)
    if feature is not None:
        return feature.to_model()
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Feature with id {feature_id} could not be found"
        )
