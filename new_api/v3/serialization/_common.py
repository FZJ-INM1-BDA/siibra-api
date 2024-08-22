from pandas import Series, DataFrame
import numpy as np

from new_api.v3.models._commons import SeriesModel, DataFrameModel


from . import instance_to_model, serialize

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
def pddf_to_model(df: DataFrame, detail: str=False, **kwargs) -> DataFrameModel:
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
