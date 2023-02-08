from api.models.locations.location import LocationModel
from api.serialization.util.siibra import Location
from api.serialization.util import serialize, instance_to_model

@serialize(Location)
def location_to_model(location: Location, **kwargs) -> LocationModel:
    return LocationModel(
        space={ "@id": location.space.id }
    )
