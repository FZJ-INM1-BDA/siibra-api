from pydantic import BaseModel, Field
from typing import List, Union

class CustomList(list):

    @staticmethod
    def serialize(instance, **kwargs):
        from app.serialization.util import instance_to_model
        from models.app.error import SerializationErrorModel
        try:
            return instance_to_model(instance, **kwargs)
        except Exception as e:
            return SerializationErrorModel(message=str(e))

    def __init__(self, full_list: List, **kwargs):
        self.full_list = full_list
        self.kwargs = kwargs
        super().__init__()

    def __len__(self):
        return len(self.full_list)

    def __getitem__(self, key: Union[int, slice]):
        try:
            of_interest = self.full_list[key]
            if isinstance(of_interest, list):
                return [CustomList.serialize(mod, **self.kwargs) for mod in of_interest]
            return CustomList.serialize(of_interest, **self.kwargs)
        except IndexError as e:
            raise e

