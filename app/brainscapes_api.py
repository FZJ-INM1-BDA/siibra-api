import json
import io
from PIL import Image
import nibabel as nib
import zipfile
import request_utils

from brainscapes import features
from brainscapes.atlas import REGISTRY
from flask import request, send_file
from flask.json import jsonify


def receptordata_fingerprint():
    if request.args and 'region' in request.args:
        receptor_data = request_utils.query_data('ReceptorDistribution', request.args['region'])
        # return json.dumps(receptor_data[0].fingerprint.__dict__)
        return jsonify(receptor_data[0].fingerprint.__dict__)
    else:
        return "A region name must be provided as a query parameter", 400


def receptordata_profiles():
    if request.args and 'region' in request.args:
        receptor_data = request_utils.query_data('ReceptorDistribution', request.args['region'])
        data = {}
        for key, profile in receptor_data[0].profiles.items():
            data[key] = profile
        return jsonify(data)
    else:
        return "A region name must be provided as a query parameter", 400


def receptordata_autoradiographs():
    if request.args and 'region' in request.args:
        receptor_data = request_utils.query_data('ReceptorDistribution', request.args['region'])
        data = {}
        for key, autoradiographs in receptor_data[0].autoradiographs.items():
            data[key] = 'PLI Image'
        return data
    else:
        return "A region name must be provided as a query parameter", 400


def parcellations():
    atlas = request_utils._create_atlas()
    parcellations = atlas.parcellations
    result = []
    for parcellation in parcellations:
        result.append({"id": parcellation.id, "name": parcellation.name})
    return jsonify(result)


def spaces():
    atlas = request_utils._create_atlas()
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
    atlas = request_utils._create_atlas()
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


def _get_file_from_nibabel(nibabel_object, nifti_type, space):
    filename = '{}-{}.nii'.format(nifti_type, space.name.replace(' ','_'))
    # save nifti file in file-object
    nib.save(nibabel_object, filename)
    return filename


def maps():
    atlas = request_utils._create_atlas()
    space = _find_space_by_id(atlas, request.args['space'])
    maps = atlas.get_maps(space)
    print(maps.keys())

    if len(maps) == 1:
        filename = _get_file_from_nibabel(maps[0], 'maps', space)
        return send_file(
            filename, 
            as_attachment=True,
            attachment_filename=filename
        )  
    else:
        files = []
        mem_zip = io.BytesIO()

        for label, space_map in maps.items():
            files.append(_get_file_from_nibabel(space_map, label, space))

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

def templates():
    atlas = request_utils._create_atlas()
    space = _find_space_by_id(atlas, request.args['space'])
    template = atlas.get_template(space)
    
    # create file-object in memory
    # file_object = io.BytesIO()
    filename = 'template-{}.nii'.format(space.name.replace(' ','_'))
    
    # save nifti file in file-object
    nib.save(template, filename)

    # file_object.seek(0)

    return send_file(
        filename, 
        as_attachment=True,
        attachment_filename=filename
    )


def genes():
    atlas = request_utils._create_atlas()
    selected_region = atlas.regiontree.find(request.args['region'])
    atlas.select_region(selected_region[0])
    if request.args['gene'] in features.gene_names:
        genes_feature = atlas.query_data(
            modality=features.modalities.GeneExpression,
            gene=request.args['gene']
        )
        result = []
        for g in genes_feature:
            result.append(dict(
                expression_levels=g.expression_levels,
                factors=g.factors,
                gene=g.gene,
                location=g.location.tolist(),
                space=g.space.id,
                z_scores=g.z_scores
            ))
        return jsonify(result)
    else:
        return 'Gene {} not found'.format(request.args['gene']), 404


