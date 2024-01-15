import pytest
from api.serialization.util.siibra import (
    LayerwiseBigBrainIntensities,
    LayerwiseCellDensity,
    GeneExpressions,
    ReceptorDensityFingerprint,
    Tabular,
)
from api.serialization.util import instance_to_model
from api.models.features._basetypes.tabular import _SiibraTabularModel

from random import random, seed
from typing import List, Any
import os

_seed = round(random() * 1000)

def get_random_n(n: int, lls: List[List[Any]]):
    seed(_seed)
    print(f"seed: {_seed}, {', '.join([str(len(ls)) for ls in lls])}")
    indicies = [round(random() * 1e6) for _ in range(n)]
    return [ ls[idx % len(ls)]
        for idx in indicies
        for ls in lls
    ]

celldensity = LayerwiseCellDensity._get_instances()
bb_intensities = LayerwiseBigBrainIntensities._get_instances()
receptor_fp_features = ReceptorDensityFingerprint._get_instances()

all_fp_features = [
    *bb_intensities[10:],
    # *celldensity[10:],
    *receptor_fp_features[10:],
] if os.environ.get("FAST_RUN") else [
    *bb_intensities,
    # *celldensity,
    *receptor_fp_features,
]

@pytest.mark.parametrize('fp', all_fp_features)
def test_fp(fp: Tabular):
    assert isinstance(fp, Tabular), f"fp should be of instance RegionalFingerprint"
    model = instance_to_model(fp)
    assert isinstance(model, _SiibraTabularModel)
    model.dict()

idx1 = round(random() * 5000)
idx2 = round(random() * 5000)

random_five_fp_features = get_random_n(5, [
    celldensity,
    # no features. re-enable once there are features
    # bb_intensities,
    receptor_fp_features
])

def test_zero_length_features():
    assert len(bb_intensities) == 0
