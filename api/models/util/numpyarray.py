from api.models._commons import ConfigBaseModel
from pydantic import Field

class NpArrayDataModel(ConfigBaseModel):
    """deprecated
    
    NpArrayDataModel"""
    
    content_type: str = Field("application/octet-stream")
    content_encoding: str = Field("gzip; base64")
    x_width: int = Field(..., alias="x-width")
    x_height: int = Field(..., alias="x-height")
    x_channel: int = Field(..., alias="x-channel")
    dtype: str
    content: str

    def __init__(self, np_data=None, **data) -> None:
        import numpy as np
        import base64
        import gzip

        if np_data is None:
            return super().__init__(**data)

        # try to avoid 64 bit any number
        supported_dtype = [
            np.dtype("uint8"),
            np.dtype("int32"),
            np.dtype("float32"),
        ]
        assert type(np_data) is np.ndarray, f"expect input to be numpy array"
        assert np_data.dtype in supported_dtype, f"can only serialize {','.join([str(dtype) for dtype in supported_dtype])} for now"
        assert len(np_data.shape) <= 3, f"can only deal np array with up to 3 dimension"
        
        x_channel = 1 if len(np_data.shape) < 3 else np_data.shape[2]
        x_width = np_data.shape[0]
        x_height = 1 if len(np_data.shape) < 2 else np_data.shape[1]
        dtype = str(np_data.dtype)
        content = base64.b64encode(gzip.compress(np_data.tobytes(order="F")))

        super().__init__(
            x_width=x_width,
            x_height=x_height,
            dtype=dtype,
            content=content,
            x_channel=x_channel,
        )
