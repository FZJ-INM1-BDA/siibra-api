"""This module handles the serialization of siibra objects into pydantic models.

Processes import from this module will require siibra installed."""

from . import (
    core,
    features,
    # util,
    volumes,
    _retrieval,
    _common,
    locations,
    # vocabularies, # For now, there are no serialization to be done on vocabolaries
)

