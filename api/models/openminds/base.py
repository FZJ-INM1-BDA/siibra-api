from pydantic import BaseModel, Field

class _BaseModel(BaseModel):
    
    def dict(self, *arg, **kwargs):
        kwargs["by_alias"] = True
        return super().dict(*arg, **kwargs)

    class Config:
        allow_population_by_field_name = True

class VocabModel(_BaseModel):
    vocab: str = Field(..., alias="@vocab")


class SiibraBaseModel(_BaseModel):
    context: VocabModel = Field(VocabModel(vocab="https://openminds.ebrains.eu/vocab/"), alias="@context")
    
