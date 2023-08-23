from api.common import data_decorator
from api.siibra_api_config import ROLE, __version__, SIIBRA_API_SHARED_DIR
from zipfile import ZipFile
import gzip
from uuid import uuid4
from pathlib import Path
from datetime import datetime

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

"""

LICENSE = """Please check the respective citations regarding licenses to use these data."""

@data_decorator(ROLE)
def download_all(space_id: str, parcellation_id: str, region_id: str=None) -> str:
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
        
        def write_model(filename, obj, **kwargs):
            try:
                zipfile.writestr(filename, instance_to_model(obj, **kwargs).json(indent=2))
            except Exception as e:
                zipfile.writestr(f"{filename}.error.txt", str(e))
        
        def write_desc(filename, obj, **kwargs):
            if isinstance(obj, _concept.AtlasConcept):
                try:
                    publications = "\n\n".join([f"[{p.get('citation', 'url')}]({p.get('url')})"
                                                if p.get('url')
                                                else p.get("citation", "CITATION")
                                                for p in obj.publications])
                    desc_str = DESC.format(name=obj.name, description=obj.description, citations=publications)
                    zipfile.writestr(filename, desc_str)
                except Exception as e:
                    zipfile.writestr(f"{filename}.error.txt", str(e))
            
        
        readme_txt = README.format(siibra_api_version=__version__,
                                   timestamp=str(datetime.now()),
                                   injected_content=f"space_id={space_id}, parcellation_id={parcellation_id}, region_id={region_id}")
        zipfile.writestr("README.md", readme_txt)
        zipfile.writestr("LICENCE.txt", LICENSE)
        try:
            space_filename = None

            space: _space.Space = siibra.spaces[space_id]
            space_filename = f"{space.key}.nii.gz"

            # this should fetch anything (surface, nifti, ng precomputed)
            space_vol = space.get_template().fetch()
            zipfile.writestr(space_filename, gzip.compress(space_vol.to_bytes()))
            write_desc(f'{space_filename}.info.md', space)
        except Exception as e:
            zipfile.writestr(f"{space_filename or 'UNKNOWN_SPACE'}.error.txt", str(e))
        

        if not region_id:
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


        if region_id:
            try:
                region_filename = None
                space: _space.Space = siibra.spaces[space_id]
                region = siibra.get_region(parcellation_id, region_id)
                region_filename = f"{region.key}.nii.gz"
                regional_map = region.fetch_regional_map(space, siibra.MapType.STATISTICAL)
                zipfile.writestr(region_filename, gzip.compress(regional_map.to_bytes()))
                write_desc(f'{region_filename}.info.md', region)
            except Exception as e:
                zipfile.writestr(f"{region_filename or 'UNKNOWN_REGION'}.error.txt", str(e))


    return str(zipfilename)
