from brainscapes.authentication import Authentication
from flask import request, send_file
from brainscapes.atlas import REGISTRY


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