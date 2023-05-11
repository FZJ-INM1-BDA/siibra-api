from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import MapIndex
from api.models._commons import MapIndexModel, SeriesModel, DataFrameModel
from pandas import Series, DataFrame
import numpy as np

@serialize(MapIndex)
def mapindex_to_model(mapindex: MapIndex, **kwargs):
    return MapIndexModel(
        volume=mapindex.volume or 0,
        label=mapindex.label,
        fragment=mapindex.fragment
    )

# will affect how dtype attribute is serialised
serializable_dtype = (
    np.dtype('int8'),
    np.dtype('int16'),
    np.dtype('int32'),
    np.dtype('int64'),
    np.dtype('float16'),
    np.dtype('float32'),
    np.dtype('float64'),
)

@serialize(Series)
def pdseries_to_model(series: Series, **kwargs):
    assert series.dtype in serializable_dtype, f"series dtype {series.dtype} not in serializable type: {', '.join([v.__name__ for v in serializable_dtype])}"
    return SeriesModel(
        name=series.name,
        dtype=str(series.dtype),
        index=[instance_to_model(el) for el in series.index],
        data=series.values.tolist()
    )

@serialize(DataFrame)
def pddf_to_model(df: DataFrame, detail=False, **kwargs):

    return DataFrameModel(
        index=[instance_to_model(el) for el in df.index],
        columns=[instance_to_model(el) for el in df.columns],
        ndim=df.ndim,
        data=instance_to_model(df.values.tolist()) if detail else None,
    )
