from fastapi.routing import APIRoute

class SapiCustomRoute(APIRoute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dependant.query_params = [ query_param
            for query_param in self.dependant.query_params
            if query_param.name != "func"
        ]

def add_lazy_path():
    """
    adds lazy_path path converter for starlette route

    For example:

    "GET /atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/Area%20hOc1%20%28V1%2C%2017%2C%20CalcS%29%20right/features/siibra%2Ffeatures%2Fcells%2Fhttps%3A%2F%2Fopenminds.ebrains.eu%2Fcore%2FDatasetVersion%2Fc1438d1996d1d2c86baa05496ba28fc5"

    or 

    ```python
    "/atlases/{atlas_id}/parcellations/{parc_id}/regions/{region_id}/features/{feat_id}".format(
        atlas_id="juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1",
        parc_id="minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290",
        region_id="Area%20hOc1%20%28V1%2C%2017%2C%20CalcS%29%20right",
        feat_id="siibra%2Ffeatures%2Fcells%2Fhttps%3A%2F%2Fopenminds.ebrains.eu%2Fcore%2FDatasetVersion%2Fc1438d1996d1d2c86baa05496ba28fc5",
    )
    ```

    default path converter (eager) will:
    1/ deserialize URI encoded characters, resulting in:
    ```python
    "/atlases/{atlas_id}/parcellations/{parc_id}/regions/{region_id}/features/{feat_id}".format(
        atlas_id="juelich/iav/atlas/v1.0.0/1",
        parc_id="minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290",
        region_id="Area hOc1 (V1, 17, CalcS) right",
        feat_id="siibra/features/cells/https://openminds.ebrains.eu/core/DatasetVersion/c1438d1996d1d2c86baa05496ba28fc5",
    )
    ```
    2/ try to eager match, resulting in errorenous parsing of the path:

    ```python
    "/atlases/{atlas_id}/parcellations/{parc_id}/regions/{region_id}/features/{feat_id}".format(
        atlas_id="juelich/iav/atlas/v1.0.0/1",
        parc_id="minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290",
        region_id="Area hOc1 (V1, 17, CalcS) right/features/siibra",
        feat_id="cells/https://openminds.ebrains.eu/core/DatasetVersion/c1438d1996d1d2c86baa05496ba28fc5",
    )
    ```

    The lazy path converter is not without its (potential) issue:

    For example:

    "GET /atlases/foo-bar/parcellations/parc%2Ffeatures%2Ffoo/features"

    or 

    ```python
    "/atlases/{atlas_id}/parcellations/{parc_id}/features".format(
        atlas_id="foo-bar",
        parc_id="parc%2Ffeatures%2Ffoo"
    )
    ```

    1/ deserialization of URI encoded characters, resulting in:

    ```python
    "/atlases/{atlas_id}/parcellations/{parc_id}/features".format(
        atlas_id="foo-bar",
        parc_id="parc/features/foo"
    )
    ```
    
    2/ trying to lazy match, resulting in errorenous parsing of the path:

    ```python
    "/atlases/{atlas_id}/parcellations/{parc_id}/features/{features_id}".format(
        atlas_id="foo-bar",
        parc_id="parc",
        features_id="foo"
    )
    ```

    Most ideally, the starlette routing should split path first, then decode the encoded characters
    """
    from starlette.convertors import PathConvertor, CONVERTOR_TYPES

    class LazyPathConverter(PathConvertor):
        regex = ".*?"

    CONVERTOR_TYPES["lazy_path"] = LazyPathConverter()
