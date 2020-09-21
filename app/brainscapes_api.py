from flask import request
from brainscapes.authentication import Authentication
from brainscapes.features import receptors


def receptordata_fingerprint():
    if request.args and 'region' in request.args:
        auth = Authentication.instance()
        auth.set_token(request.args['token'])
        receptor_data = receptors.get_receptor_data_by_region(request.args['region'])
        return receptor_data.fingerprint.to_json()
    else:
        return "A region name must be provided as a query parameter", 400


def receptordata_profiles():
    if request.args and 'region' in request.args:
        auth = Authentication.instance()
        auth.set_token(request.args['token'])
        receptor_data = receptors.get_receptor_data_by_region(request.args['region'])
        data = {}
        for key, profile in receptor_data.profiles.items():
            data[key] = profile.to_json()
        return data
    else:
        return "A region name must be provided as a query parameter", 400


def receptordata_autoradiographs():
    if request.args and 'region' in request.args:
        auth = Authentication.instance()
        auth.set_token(request.args['token'])
        receptor_data = receptors.get_receptor_data_by_region(request.args['region'])
        return receptor_data.autoradiographs_files
    else:
        return "A region name must be provided as a query parameter", 400

