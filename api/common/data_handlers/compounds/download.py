from api.common import data_decorator
from api.siibra_api_config import ROLE, __version__, SIIBRA_API_SHARED_DIR
from zipfile import ZipFile
import gzip
from uuid import uuid4
from pathlib import Path

README = """# Packaged Atlas Data

This zip is automatically packaged by siibra-api {siibra_api_version}. For any bug reports/suggestions, you can do one of the following:

- file a bug with us directly at [https://github.com/FZJ-INM1-BDA/siibra-api/issues](https://github.com/FZJ-INM1-BDA/siibra-api/issues)
- email [support@ebrains.eu](mailto:support@ebrains.eu) with the subject line `atlas support / siibra-api`

In either case, please describe your issue and include the following code snippit:

```
{injected_content}
```

"""

@data_decorator(ROLE)
def download_all(space_id: str, parcellation_id: str, region_id: str=None):
    zipfilename = Path(SIIBRA_API_SHARED_DIR, f"atlas-download-{str(uuid4())}.zip")

    import siibra
    from api.serialization.util import instance_to_model
    from siibra.core import space as _space, parcellation as _parcellation

    with ZipFile(zipfilename, "w") as zipfile:
        
        zipfile.writestr("README.md", README.format(siibra_api_version=__version__, injected_content=f"space_id={space_id}, parcellation_id={parcellation_id}, region_id={region_id}"))

        try:
            filename = "template/template.nii.gz"
            space: _space.Space = siibra.spaces[space_id]

            # Only fetch niftis for now
            # TODO bug in siibra-python. for now, try nii first, if None, try zip/nii
            # see https://github.com/FZJ-INM1-BDA/siibra-python/issues/386
            space_vol = space.get_template().fetch(format="nii") or space.get_template().fetch(format="zip/nii")
            zipfile.writestr(filename, gzip.compress(space_vol.to_bytes()))
        except Exception as e:
            zipfile.writestr(f"{filename}.error.txt", str(e))
        
        try:
            filename = "parcellation/parcellation.nii.gz"
            space: _space.Space = siibra.spaces[space_id]
            parcellation: _parcellation.Parcellation = siibra.parcellations[parcellation_id]

            parc_vol = parcellation.get_map(space, siibra.MapType.LABELLED).fetch()
            zipfile.writestr(filename, gzip.compress(parc_vol.to_bytes()))
        except Exception as e:
            zipfile.writestr(f"{filename}.error.txt", str(e))

        if region_id:
            try:
                filename = "region/region.nii.gz"
                space: _space.Space = siibra.spaces[space_id]
                region = parcellation.get_region(region_id) if region_id else None
                regional_map = region.fetch_regional_map(space, siibra.MapType.STATISTICAL)
                zipfile.writestr(filename, gzip.compress(regional_map.to_bytes()))
            except Exception as e:
                zipfile.writestr(f"{filename}.error.txt", str(e))

    return str(zipfilename)

class RequiredParamMissing(Exception): pass

__all__ = [
    "download_all"
]
