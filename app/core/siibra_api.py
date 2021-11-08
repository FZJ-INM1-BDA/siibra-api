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
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic.main import BaseModel
import siibra
from siibra.core.jsonable import SiibraSerializable

# FastApi router to create rest endpoints
router = APIRouter()


@router.get('/genes',
            tags=['data'],
            response_model=List[str])
def get_gene_names():
    """
    # Returns all gene names

    Return all genes (name, acronym) in siibra

    ## code sample

    ```python
    import siibra
    gene_names: List[str] = [name for name in siibra.features.gene_names]
    ```
    """
    return [ g for g in siibra.features.gene_names ]


class ModalitySchema(BaseModel):
    name: str
    supported: bool


@router.get('/features',
            tags=['data'],
            response_model=List[ModalitySchema])
def get_all_available_modalities():
    """
    # List of all possible modalities

    Return all possible modalities, and if they are supported in siibra-api.

    ## code sample
    ```python
    import siibra

    siibra.features.modalities
    ```
    """
    return [ ModalitySchema(name=mod.modality(), supported=issubclass(mod._FEATURETYPE, SiibraSerializable))
        for mod in siibra.features.modalities]
