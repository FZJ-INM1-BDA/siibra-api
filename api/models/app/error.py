from pydantic import BaseModel, Field

class SerializationErrorModel(BaseModel):
    type: str = Field("spy/serialization-error", const=True)
    message: str
