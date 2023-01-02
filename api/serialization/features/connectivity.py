from api.serialization.util import serialize
from app import logger
from siibra.features.connectivity import ConnectivityMatrix
from api.models.features.connectivity import ConnectivityMatrixDataModel
from api.models.util import NpArrayDataModel
from typing import Union

@serialize(ConnectivityMatrix)
def connmatrix_to_model(matrix: ConnectivityMatrix, *, detail: bool=False, **kwargs) -> ConnectivityMatrixDataModel:

    # these properties do not exist on ConnectivityMatrix, but may be populated from ConnectivityMatrix.src_info via __getattr__
    model_dict_from_getattr = {
        key: getattr(matrix, key) if hasattr(matrix, key) else None
        for key in [
            "name",
            "description",
            "citation",
            "authors",
            "cohort",
            "subject",
            "filename",
            "dataset_id",
        ]
    }

    base_model = ConnectivityMatrixDataModel(
        id=matrix.id,
        type="siibra/features/connectivity",
        parcellations=[
            {
                "@id": parc.id,
            }
            for parc in matrix.parcellations
        ],
        **model_dict_from_getattr,
    )

    if detail is False:
        return base_model
    
    from siibra.core import Region
    import numpy as np

    dtype_set = {dtype for dtype in matrix.matrix.dtypes}

    if len(dtype_set) == 0:
        raise TypeError("dtype is an empty set!")

    force_float = False
    if len(dtype_set) == 1:
        (dtype,) = list(dtype_set)
        is_int = np.issubdtype(dtype, int)
        is_float = np.issubdtype(dtype, float)
        assert (
            is_int or is_float
        ), f"expect datatype to be subdtype of either int or float, but is neither: {str(dtype)}"

    if len(dtype_set) > 1:
        logger.warning(
            f"expect only 1 type of data, but got {len(dtype_set)}, will cast everything to float"
        )
        force_float = True

    def get_column_name(col: Union[str, Region]) -> str:
        if isinstance(col, str):
            return col
        if isinstance(col, Region):
            return col.name
        raise TypeError(
            f"matrix column value {col} of instance {col.__class__} can be be converted to str."
        )

    base_model.columns = [
        get_column_name(name) for name in matrix.matrix.columns.values
    ]
    base_model.matrix = NpArrayDataModel(
        matrix.matrix.to_numpy(
            dtype="float32" if force_float or is_float else "int32"
        )
    )
    return base_model
