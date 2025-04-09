from api.common import data_decorator
from api.siibra_api_config import ROLE, __version__, SIIBRA_API_SHARED_DIR
from zipfile import ZipFile
import gzip
from uuid import uuid4
from pathlib import Path
from datetime import datetime
import json
import math

BIGBRAIN_ID = "minds/core/referencespace/v1.0.0/a1655b99-82f1-420f-a3c2-fe80fd4c8588"
BIGBRAIN_SIZE_LIMIT = 2 * 1024 * 1024

README = """# Packaged Atlas Data

This zip is automatically packaged by siibra-api {siibra_api_version}, retrieved on {timestamp}. For any bug reports/suggestions, you can do one of the following:

- file a bug with us directly at [https://github.com/FZJ-INM1-BDA/siibra-api/issues](https://github.com/FZJ-INM1-BDA/siibra-api/issues)
- email [support@ebrains.eu](mailto:support@ebrains.eu) with the subject line `atlas support / siibra-api`

In either case, please describe your issue and include the following code snippit:

```
{injected_content}
```

"""

DESC = """name:
---

{name}

description:
---

{description}

citations:
---
{citations}

license:
---
{license}

"""

LICENSE = """Please check the respective `.info.md` regarding licenses of the data."""

@data_decorator(ROLE)
def download_all(space_id: str=None, parcellation_id: str=None, region_id: str=None, feature_id: str=None, bbox=None) -> str:
    """Create a download bundle (zip) for the provided specification
    
    Args:
        space_id: lookup id of the space requested
        parcellation_id: lookup_id of the parcellation requested
        region_id: lookup_id of the region requested
    
    Returns:
        Path to the zip file

    """
    zipfilename = Path(SIIBRA_API_SHARED_DIR, f"atlas-download-{str(uuid4())}.zip")

    import siibra
    from api.serialization.util import instance_to_model
    from siibra.core import space as _space, parcellation as _parcellation, concept as _concept

    with ZipFile(zipfilename, "w") as zipfile:

        if feature_id:
            try:
                path_to_feature_export = Path(SIIBRA_API_SHARED_DIR, f"export-{feature_id}.zip")
                if not path_to_feature_export.exists():
                    feature = siibra.features.Feature.get_instance_by_id(feature_id)
                    feature.export(path_to_feature_export)
                zipfile.write(path_to_feature_export, f"export-{feature_id}.zip")
            except Exception as e:
                zipfile.writestr(f"{feature_id}.error.txt", f"Feature exporting failed: {str(e)}")
        
        def write_model(filename, obj, **kwargs):
            try:
                zipfile.writestr(filename, instance_to_model(obj, **kwargs).json(indent=2))
            except Exception as e:
                zipfile.writestr(f"{filename}.error.txt", str(e))

        def write_desc(filename, obj, **kwargs):
            try:
                space = kwargs.get("space")
                if space is not None and isinstance(obj, siibra.core.parcellation.region.Region):
                    assert isinstance(space, _space.Space)
                    mp = siibra.get_map(obj.parcellation, space, "statistical")
                    volidx = mp.get_index(obj)
                    vol = mp.volumes[volidx.volume]
                    publications = "\n\n".join([
                        f"[{url.get('citation', 'url')}]({url.get('url')})"
                        for ds in vol.datasets
                        for url in ds.urls
                    ])
                    desc = "\n\n".join([ds.description for ds in vol.datasets])
                    license_list = []
                    for ds in vol.datasets:
                        if isinstance(ds.LICENSE, list):
                            license_list.extend(ds.LICENSE)
                        if isinstance(ds.LICENSE, str):
                            license_list.append(ds.LICENSE)
                        
                    license = "\n\n".join(license_list)
                    desc_str = DESC.format(name=f"Statistical map of {obj.name} in {space.name}",
                                           description=desc,
                                           citations=publications,
                                           license=license)
                    zipfile.writestr(filename, desc_str)
                    return
                if isinstance(obj, _concept.AtlasConcept):
                    publications = "\n\n".join([f"[{p.get('citation', 'url')}]({p.get('url')})"
                                                if p.get('url')
                                                else p.get("citation", "CITATION")
                                                for p in obj.publications])
                    desc_str = DESC.format(name=obj.name, description=obj.description, citations=publications, license=obj.LICENSE)
                    zipfile.writestr(filename, desc_str)
                    return
            except Exception as e:
                zipfile.writestr(f"{filename}.error.txt", str(e))
        
        if space_id is not None:
            injected_content=f"space_id={space_id}, parcellation_id={parcellation_id}, region_id={region_id}, bbox={bbox}"

            readme_txt = README.format(siibra_api_version=__version__,
                                    timestamp=str(datetime.now()),
                                    injected_content=injected_content)
            zipfile.writestr("README.md", readme_txt)
            zipfile.writestr("LICENCE.txt", LICENSE)
            try:
                space_filename = None

                space: _space.Space = siibra.spaces[space_id]
                space_filename = f"{space.key}.nii.gz"

                # this should fetch anything (surface, nifti, ng precomputed)
                if space.id == BIGBRAIN_ID:
                    if bbox:
                        bounding_box = space.get_bounding_box(*json.loads(bbox))
                        value = BIGBRAIN_SIZE_LIMIT
                        for dim in bounding_box.maxpoint - bounding_box.minpoint:
                            value /= dim
                        cube_rooted = math.pow(value, 1/3)
                        space_vol = space.get_template().fetch(voi=bounding_box, resolution_mm=1/cube_rooted)
                    else:
                        raise RuntimeError(f"For big brain, bbox must be defined.")
                else:
                    space_vol = space.get_template().fetch()
                zipfile.writestr(space_filename, gzip.compress(space_vol.to_bytes()))
                write_desc(f'{space_filename}.info.md', space)
            except Exception as e:
                zipfile.writestr(f"{space_filename or 'UNKNOWN_SPACE'}.error.txt", str(e))
            
        if parcellation_id is not None:
            if region_id is None:
                try:
                    parc_filename = None
                    space: _space.Space = siibra.spaces[space_id]
                    parcellation: _parcellation.Parcellation = siibra.parcellations[parcellation_id]
                    parc_filename = f"{parcellation.key}.nii.gz"

                    parc_vol = parcellation.get_map(space, siibra.MapType.LABELLED).fetch()
                    zipfile.writestr(parc_filename, gzip.compress(parc_vol.to_bytes()))
                    write_desc(f'{parc_filename}.info.md', parcellation)
                except Exception as e:
                    zipfile.writestr(f"{parc_filename or 'UNKNOWN_PARCELLATION'}.error.txt", str(e))


            if region_id is not None:
                try:
                    region_filename = None
                    space: _space.Space = siibra.spaces[space_id]
                    region = siibra.get_region(parcellation_id, region_id)
                    region_filename = f"{region.key}.nii.gz"
                    regional_map = region.fetch_regional_map(space, siibra.MapType.STATISTICAL)
                    zipfile.writestr(region_filename, gzip.compress(regional_map.to_bytes()))
                    write_desc(f'{region_filename}.info.md', region, space=space)
                except Exception as e:
                    zipfile.writestr(f"{region_filename or 'UNKNOWN_REGION'}.error.txt", str(e))


    return str(zipfilename)
