from api.common import data_decorator
from api.siibra_api_config import ROLE, __version__, SIIBRA_API_SHARED_DIR
from zipfile import ZipFile
import gzip
from uuid import uuid4
from pathlib import Path
from datetime import datetime
import json
import math
import requests

VOLUME_SIZE_LIMIT = 2 * 1024 * 1024

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

def download_region(space_id: str, parcellation_id: str, region_id: str, * , zipfile: ZipFile, **kwargs):
    import siibra
    from siibra.core import space as _space
    
    try:
        region_filename = None
        space: _space.Space = siibra.spaces[space_id]
        region = siibra.get_region(parcellation_id, region_id)
        region_filename = f"{region.key}.nii.gz"
        regional_map = region.fetch_regional_map(space, siibra.MapType.STATISTICAL)
        zipfile.writestr(region_filename, gzip.compress(regional_map.to_bytes()))


    except Exception as e:
        zipfile.writestr(f"{region_filename or 'UNKNOWN_REGION'}.error.txt", str(e))

    # desc
    try:
        mp = siibra.get_map(parcellation_id, space, "statistical")
        volidx = mp.get_index(region)
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
        desc_str = DESC.format(name=f"Statistical map of {region.name} in {space.name}",
                                description=desc,
                                citations=publications,
                                license=license)
        zipfile.writestr(f'{region_filename}.info.md', desc_str)
    except Exception as e:
        zipfile.writestr(f'{region_filename}.info.md.error.txt', str(e))

def download_parcellation(space_id: str, parcellation_id: str, * , zipfile: ZipFile, **kwargs):
    import siibra
    from siibra.core import space as _space, parcellation as _parcellation
    
    try:
        parc_filename = None
        space: _space.Space = siibra.spaces[space_id]
        parcellation: _parcellation.Parcellation = siibra.parcellations[parcellation_id]
        parc_filename = f"{parcellation.key}.label.nii.gz"

        parc_vol = parcellation.get_map(space, siibra.MapType.LABELLED).fetch()
        zipfile.writestr(parc_filename, gzip.compress(parc_vol.to_bytes()))

    except Exception as e:
        zipfile.writestr(f"{parc_filename or 'UNKNOWN_PARCELLATION'}.error.txt", str(e))

    info_filename = f'{parc_filename or "UNKNOWN_PARCELLATION"}.info.md'
    try:
        publications = "\n\n".join([f"[{p.get('citation', 'url')}]({p.get('url')})"
                                    if p.get('url')
                                    else p.get("citation", "CITATION")
                                    for p in parcellation.publications])
        desc_str = DESC.format(name=parcellation.name,
                               description=parcellation.description,
                               citations=publications,
                               license=parcellation.LICENSE)
        zipfile.writestr(info_filename, desc_str)
    except Exception as e:
        zipfile.writestr(f"{info_filename}.error.txt", str(e))

def download_space(space_id: str, bbox: str, * , zipfile: ZipFile):
    import siibra
    from siibra.core import space as _space
    try:
        space_filename = None

        space: _space.Space = siibra.spaces[space_id]
        space_filename = space.key

        template = space.get_template()

        if "neuroglancer/precomputed" in template.formats:
            space_filename += ".nii.gz"
            if bbox is None:
                bbox = template.boundingbox
            bounding_box = space.get_bounding_box(*json.loads(bbox))
            value = VOLUME_SIZE_LIMIT
            for dim in bounding_box.maxpoint - bounding_box.minpoint:
                value /= dim
            cube_rooted = math.pow(value, 1/3)
            space_vol = template.fetch(voi=bounding_box,
                                        format="neuroglancer/precomputed",
                                        resolution_mm=1/cube_rooted)
            zipfile.writestr(space_filename, gzip.compress(space_vol.to_bytes()))
        if "gii-mesh" in template.formats:
            for idx, vol in enumerate(space.volumes):
                variant = vol.variant or f'unknown-variant-{idx}'
                root = f"{space_filename}/{variant}"
                if "gii-mesh" in vol.providers:
                    url = vol.providers["gii-mesh"]
                    def write_url(base_path: str, url: str):
                        filename = "unknownfile"
                        try:
                            filepath = Path(url)
                            filename = filepath.name
                            resp = requests.get(url)
                            resp.raise_for_status()

                            zipfile.writestr(f"{base_path}/{filename}", resp.content)
                        except Exception as e:
                            zipfile.writestr(f"{base_path}/{filename}.error.txt", str(e))
                    if isinstance(url, str):
                        write_url(root, url)
                    if isinstance(url, dict):
                        for key, _url in url.items():
                            write_url(f"{root}/{key}", _url)

    except Exception as e:
        zipfile.writestr(f"{space_filename or 'UNKNOWN_SPACE'}.error.txt", str(e))
    
    info_filename = f'{space_filename or "UNKNOWN_PARCELLATION"}.info.md'
    try:
        publications = "\n\n".join([f"[{p.get('citation', 'url')}]({p.get('url')})"
                                    if p.get('url')
                                    else p.get("citation", "CITATION")
                                    for p in space.publications])
        desc_str = DESC.format(name=space.name,
                               description=space.description,
                               citations=publications,
                               license=space.LICENSE)
        zipfile.writestr(info_filename, desc_str)
    except Exception as e:
        zipfile.writestr(f"{info_filename}.error.txt", str(e))


@data_decorator(ROLE)
def download_all(space_id: str=None, parcellation_id: str=None, region_id: str=None, feature_id: str=None, bbox: str=None, strict_mode: str=None) -> str:
    """Create a download bundle (zip) for the provided specification
    
    Args:
        space_id: lookup id of the space requested
        parcellation_id: lookup_id of the parcellation requested
        region_id: lookup_id of the region requested
    
    Returns:
        Path to the zip file

    """
    zipfilename = Path(SIIBRA_API_SHARED_DIR, f"atlas-download-{str(uuid4())}.zip")
    output_credit = 1 if strict_mode else 1e10

    import siibra

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

        injected_content=f"space_id={space_id}, parcellation_id={parcellation_id}, region_id={region_id}, bbox={bbox}"

        readme_txt = README.format(siibra_api_version=__version__,
                                    timestamp=str(datetime.now()),
                                    injected_content=injected_content)
        zipfile.writestr("README.md", readme_txt)
        zipfile.writestr("LICENCE.txt", LICENSE)

        if region_id is not None:
            if output_credit >= 1:
                download_region(space_id, parcellation_id, region_id, bbox=bbox, zipfile=zipfile)
                output_credit -= 1

        if parcellation_id is not None:
            if output_credit >= 1:
                download_parcellation(space_id, parcellation_id, bbox=bbox, zipfile=zipfile)
                output_credit -= 1

        if space_id is not None:
            if output_credit >= 1:
                download_space(space_id, bbox=bbox, zipfile=zipfile)
                output_credit -= 1

    return str(zipfilename)
