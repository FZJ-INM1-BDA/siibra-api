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

import siibra
from fastapi import HTTPException


def validate_and_return_atlas(atlas_id):
    """
    Check if the given atlas id is valid and return an atlas object
    If the atlas id is not valid, throw a HTTP 400 Exception

    :param atlas_id: id that needs to be checked
    :return: siibra atlas object
    """
    try:
        return siibra.atlases[atlas_id]
    except:
        raise HTTPException(
            status_code=400,
            detail=f'atlas_id: {atlas_id} is not known'
        )


def validate_and_return_space(space_id):
    """
    Check if the given space id is valid and return a space object
    If the space id is not valid, throw a HTTP 400 Exception

    :param space_id: id that needs to be checked
    :return: siibra space object
    """
    try:
        return siibra.spaces[space_id]
    except:
        raise HTTPException(
            status_code=400,
            detail=f'space_id: {space_id} is not known'
        )


def validate_and_return_parcellation(parcellation_id):
    """
    Check if the given parcellation id is valid and return a parcellation object
    If the parcellation id is not valid, throw a HTTP 400 Exception

    :param parcellation_id: id that needs to be checked
    :return: siibra parcellation object
    """
    try:
        return siibra.parcellations[parcellation_id]
    except:
        raise HTTPException(
            status_code=400,
            detail=f'parcellation_id: {parcellation_id} is not known'
        )
