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

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi import Request

import request_utils

from brainscapes import features
from flask import send_file

router = APIRouter()


@router.get('/receptors/fingerprint')
def receptordata_fingerprint(request: Request):
    """
    GET /receptors/fingerprint
    parameters: 
    - region

    Returns a fingerprint based on the provided region.
    """
    if request.args and 'region' in request.args:
        receptor_data = request_utils.query_data('ReceptorDistribution', request.args['region'])
        return jsonable_encoder(receptor_data[0].fingerprint.__dict__)
    else:
        return "A region name must be provided as a query parameter", 400

@router.get('/receptors/profiles')
def receptordata_profiles(request: Request):
    """
    GET /receptors/profiles
    parameters: 
    - region

    Returns profles based on the provided region.
    """    
    if request.args and 'region' in request.args:
        receptor_data = request_utils.query_data('ReceptorDistribution', request.args['region'])
        data = {}
        for key, profile in receptor_data[0].profiles.items():
            data[key] = profile
        return jsonable_encoder(data)
    else:
        return "A region name must be provided as a query parameter", 400

@router.get('/receptors/autoradiographs')
def receptordata_autoradiographs(request: Request):
    """
    GET /receptors/autoradiographs
    Parameters: 
    - region

    Returns autoradiographs based on the provided region.
    """    
    if request.args and 'region' in request.args:
        receptor_data = request_utils.query_data('ReceptorDistribution', request.args['region'])
        data = {}
        for key, autoradiographs in receptor_data[0].autoradiographs.items():
            data[key] = 'PLI Image'
        return data
    else:
        return "A region name must be provided as a query parameter", 400


@router.get('/parcellations')
def parcellations():
    """
    GET /parcellations

    Returns all parcellations that are defined in the brainscapes client.
    """    
    atlas = request_utils.create_atlas()
    parcellations = atlas.parcellations
    result = []
    for parcellation in parcellations:
        result.append({"id": parcellation.id, "name": parcellation.name})
    return jsonable_encoder(result)


@router.get('/spaces')
def spaces():
    """
    GET /spaces

    Returns all spaces that are defined in the brainscapes client.
    """
    atlas = request_utils.create_atlas()
    atlas_spaces = atlas.spaces
    result = []
    for space in atlas_spaces:
        result.append({"id": space.id, "name": space.name})
    return jsonable_encoder(result)


@router.get('/regions')
def regions():
    """
    GET /regions
    Parameters: 
    - parcellation

    Returns all regions for a given parcellation id.
    """
    atlas = request_utils.create_atlas()
    result = []
    for region in atlas.regiontree.children:
        region_json = {'name': region.name, 'children': []}
        request_utils._add_children_to_region(region_json, region)
        result.append(region_json)
    return result


@router.get('/maps')
def maps(request: Request):
    """
    GET /maps
    Parameters: 
    - space

    Returns all maps for a given space id.
    """
    atlas = request_utils.create_atlas()
    space = request_utils._find_space_by_id(atlas, request.args['space'])
    maps = atlas.get_maps(space)
    print(maps.keys())

    if len(maps) == 1:
        filename = request_utils._get_file_from_nibabel(maps[0], 'maps', space)
        return send_file(
            filename, 
            as_attachment=True,
            attachment_filename=filename
        )  
    else:
        files = []
        mem_zip = io.BytesIO()

        for label, space_map in maps.items():
            files.append(request_utils._get_file_from_nibabel(space_map, label, space))

        with zipfile.ZipFile(mem_zip, mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.write(f)
                print(zf.namelist())

        mem_zip.seek(0)
        return send_file(
            mem_zip, 
            as_attachment=True,
            attachment_filename='maps-{}.zip'.format(space.name.replace(' ','_'))
        ) 
        
    return 'Maps for space: {} not found'.format(space.name), 404


@router.get('/templates')
def templates(request: Request):
    """
    GET /templates
    Parameters: 
    - space

    Returns all templates for a given space id.
    """    
    atlas = request_utils.create_atlas()
    space = request_utils._find_space_by_id(atlas, request.args['space'])
    template = atlas.get_template(space)
    
    # create file-object in memory
    # file_object = io.BytesIO()
    filename = request_utils._get_file_from_nibabel(template, 'template', space)
    
    return send_file(
        filename, 
        as_attachment=True,
        attachment_filename=filename
    )


@router.get('/genes')
def genes(request: Request):
    """
    GET /genes
    Parameters: 
    - region 
    - gene

    Returns all genes for a given region and gene type.
    """    
    atlas = request_utils.create_atlas()
    selected_region = atlas.regiontree.find(request.args['region'], exact=False)

    result = []
    if request.args['gene'] in features.gene_names:
        for region in selected_region:
            atlas.select_region(region)
            genes_feature = atlas.query_data(
                modality=features.modalities.GeneExpression,
                gene=request.args['gene']
            )
            region_result = []
            for g in genes_feature:
                region_result.append(dict(
                    expression_levels=g.expression_levels,
                    factors=g.factors,
                    gene=g.gene,
                    location=g.location.tolist(),
                    space=g.space.id,
                    z_scores=g.z_scores
                ))
            result.append(dict(
                region=region.name,
                features=region_result
            ))
        return jsonable_encoder(result)
    else:
        return 'Gene {} not found'.format(request.args['gene']), 404
