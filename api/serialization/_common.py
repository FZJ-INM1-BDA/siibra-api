from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import MapIndex
from api.models._commons import MapIndexModel, SeriesModel, DataFrameModel, TimedeltaModel
from pandas import Series, DataFrame, Timedelta
import numpy as np

@serialize(MapIndex)
def mapindex_to_model(mapindex: MapIndex, **kwargs) -> MapIndexModel:
    """Serialize MapIndex instance
    
    Args:
        mapindex: instance to be serialized
    
    Returns:
        MapIndexModel
        """
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
def pdseries_to_model(series: Series, **kwargs) -> SeriesModel:
    """Serialize pandas series.
    
    Args:
        series: Series instance to be serialized
    
    Returns:
        SeriesModel
    
    Raises:
        AssertionError: if dtype is not serializable
    """

    assert series.dtype in serializable_dtype, f"series dtype {series.dtype}" + \
        "not in serializable type: {', '.join([v.__name__ for v in serializable_dtype])}"
    return SeriesModel(
        name=series.name,
        dtype=str(series.dtype),
        index=[instance_to_model(el) for el in series.index],
        data=series.values.tolist()
    )

@serialize(DataFrame)
def pddf_to_model(df: DataFrame, detail: bool=False, **kwargs) -> DataFrameModel:
    """Serialize pandas dataframe
    
    Args:
        df: DataFrame instance to be serialized
        detail: defailt flag. If not set, data attribute will not be populated.
    
    Returns:
        DataFrameModel
    """
    return DataFrameModel(
        index=[instance_to_model(el) for el in df.index],
        columns=[instance_to_model(el) for el in df.columns],
        ndim=df.ndim,
        data=instance_to_model(df.values.tolist()) if detail else None,
    )

@serialize(Timedelta)
def pdtd_to_model(dti: Timedelta, detail: bool=False, **kwargs) -> TimedeltaModel:
    return TimedeltaModel(
        total_seconds=dti.total_seconds()
    )
