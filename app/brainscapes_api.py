import json


from brainscapes.atlas import REGISTRY
from flask import request
from flask.json import jsonify
from brainscapes.authentication import Authentication


class BrainscapesJsonEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def _set_auth_token():
    auth = Authentication.instance()
    bearer_token = request.headers.get("Authorization")
    if bearer_token:
        auth.set_token(bearer_token.replace("Bearer ", ""))
    elif request.args['token']:
        auth.set_token(request.args['token'])


def _create_atlas():
    return REGISTRY.MULTILEVEL_HUMAN_ATLAS


def query_data(modality, regionname, args=None):
    _set_auth_token()
    atlas = _create_atlas()
    selected_region = atlas.regiontree.find(regionname)
    atlas.select_region(selected_region[0])
    return atlas.query_data(modality)


def receptordata_fingerprint():
    if request.args and 'region' in request.args:
        receptor_data = query_data('ReceptorDistribution', request.args['region'])
        # return json.dumps(receptor_data[0].fingerprint.__dict__)
        return jsonify(receptor_data[0].fingerprint.__dict__)
    else:
        return "A region name must be provided as a query parameter", 400


def receptordata_profiles():
    if request.args and 'region' in request.args:
        receptor_data = query_data('ReceptorDistribution', request.args['region'])
        data = {}
        for key, profile in receptor_data[0].profiles.items():
            data[key] = profile
        return jsonify(data)
    else:
        return "A region name must be provided as a query parameter", 400


def receptordata_autoradiographs():
    if request.args and 'region' in request.args:
        receptor_data = query_data('ReceptorDistribution', request.args['region'])
        data = {}
        for key, autoradiographs in receptor_data[0].autoradiographs.items():
            data[key] = 'PLI Image'
        return data
    else:
        return "A region name must be provided as a query parameter", 400


def parcellations():
    atlas = _create_atlas()
    parcellations = atlas.parcellations
    result = []
    for parcellation in parcellations:
        result.append({"id": parcellation.id, "name": parcellation.name})
    return jsonify(result)


def spaces():
    atlas = _create_atlas()
    atlas_spaces = atlas.spaces
    result = []
    for space in atlas_spaces:
        result.append({"id": space.id, "name": space.name})
    return jsonify(result)


def _add_children_to_region(region_json, region):
    for child in region.children:
        o = {'name': child.name, 'children': []}
        if child.children:
            _add_children_to_region(o, child)
        region_json['children'].append(o)


def regions():
    atlas = _create_atlas()
    result = []
    for region in atlas.regiontree.children:
        region_json = {'name': region.name, 'children': []}
        _add_children_to_region(region_json, region)
        result.append(region_json)
    return result


def _find_space_by_id(atlas, space_id):
    for space in atlas.spaces:
        if space.id == space_id:
            return space
    return {}


def maps():
    atlas = _create_atlas()
    space = _find_space_by_id(atlas, request.args['space'])
    # return atlas.get_maps(space)
    return {'result': 'Nifti data as json / binary or file url'}

def templates():
    atlas = _create_atlas()
    space = _find_space_by_id(atlas, request.args['space'])
    # return atlas.get_template(space)
    return {'result': 'Nifti data as json / binary or file url'}


def genes():
    atlas = _create_atlas()
    selected_region = atlas.regiontree.find(request.args['region'])
    atlas.select_region(selected_region[0])
    # genes_feature = atlas.query_data('GeneExpression', )
    genes_feature = atlas.query_data('GeneExpression', gene=request.args['gene'])
    return genes_feature



