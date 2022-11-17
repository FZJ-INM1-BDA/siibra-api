import pytest

from siibra import REGISTRY
from siibra.features.bigbrain import (
    WagstylBigBrainIntensityFingerprintQuery,
    WagstylBigBrainProfileQuery
)
from siibra.features.cells import (
    CellDensityFingerprint,
    CellDensityProfile,
)
from siibra.features.receptors import (
    ReceptorFingerprint,
    ReceptorDensityProfile,
)
from siibra.features.feature import (
    RegionalFingerprint,
    CorticalProfile,
)

from app.serialization.util import instance_to_model
from models.features.feature import (
    RegionalFingerprintModel,
    CorticalProfileModel,
)
from random import random, seed
from typing import List, Any
import os

_seed = round(random() * 1000)

def get_random_n(n: int, lls: List[List[Any]]):    
    seed(_seed)
    print(f"seed: {_seed}")
    indicies = [round(random() * 1e6) for _ in range(n)]
    return [ ls[idx % len(ls)]
        for idx in indicies
        for ls in lls
    ]

bigbrain_query = WagstylBigBrainIntensityFingerprintQuery()
bigbrain_fp_features = bigbrain_query.features

cell_fp_features = [f for f in REGISTRY[CellDensityFingerprint]]
receptor_fp_features = [f for f in REGISTRY[ReceptorFingerprint]]

all_fp_features = [
    *bigbrain_fp_features[10:],
    *cell_fp_features[10:],
    *receptor_fp_features[10:],
] if os.environ.get("FAST_RUN") else [
    *bigbrain_fp_features,
    *cell_fp_features,
    *receptor_fp_features,
]

@pytest.mark.parametrize('fp', all_fp_features)
def test_fp(fp: RegionalFingerprint):
    assert isinstance(fp, RegionalFingerprint), f"fp should be of instance RegionalFingerprint"
    model = instance_to_model(fp)
    assert isinstance(model, RegionalFingerprintModel)
    model.dict()

idx1 = round(random() * 5000)
idx2 = round(random() * 5000)

random_five_fp_features = get_random_n(5, [bigbrain_fp_features, cell_fp_features, receptor_fp_features])

@pytest.mark.parametrize('fp', random_five_fp_features)
def test_detail(fp: RegionalFingerprint):
    print(f"indicies: {idx1} {idx2}")
    model = instance_to_model(fp, detail=True)
    assert isinstance(model, RegionalFingerprintModel)
    assert model.data
    model.dict()


bb_query = WagstylBigBrainProfileQuery()
bb_pr_features = bb_query.features

cell_pr_features = [f for f in REGISTRY[CellDensityProfile]]
receptor_pr_features = [f for f in REGISTRY[ReceptorDensityProfile]]

all_pr_features = [
    *bb_pr_features[:10],
    *cell_pr_features[:10],
    *receptor_pr_features[:10],
] if os.environ.get("FAST_RUN") else [
    *bb_pr_features,
    *cell_pr_features,
    *receptor_pr_features,
]

@pytest.mark.parametrize('pr', all_pr_features)
def test_pr(pr: CorticalProfile):
    assert isinstance(pr, CorticalProfile)
    model = instance_to_model(pr)
    assert isinstance(model, CorticalProfileModel)
    model.dict()

random_five_pr_features = get_random_n(5, [
    bb_pr_features,
    cell_pr_features,
    receptor_pr_features,
])

@pytest.mark.parametrize('pr', random_five_pr_features)
def test_pr_detail(pr: CorticalProfile):
    model = instance_to_model(pr, detail=True)
    assert isinstance(model, CorticalProfileModel)
    assert model.data
    model.dict()

