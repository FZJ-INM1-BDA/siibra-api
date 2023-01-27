# import pytest
# from api.serialization.util.siibra import (
#     BigBrainIntensityProfile,
#     CellDensityProfile,
#     ReceptorDensityFingerprint,
#     Tabular,
# )
# from api.serialization.util import instance_to_model
# from api.models.features._basetypes.tabular import SiibraTabularModel

# from random import random, seed
# from typing import List, Any
# import os

# _seed = round(random() * 1000)

# def get_random_n(n: int, lls: List[List[Any]]):    
#     seed(_seed)
#     print(f"seed: {_seed}")
#     indicies = [round(random() * 1e6) for _ in range(n)]
#     return [ ls[idx % len(ls)]
#         for idx in indicies
#         for ls in lls
#     ]


# idx1 = round(random() * 5000)
# idx2 = round(random() * 5000)


# random_five_fp_features = get_random_n(5, [receptor_fp_features])

# @pytest.mark.parametrize('fp', random_five_fp_features)
# def test_detail(fp: Tabular):
#     print(f"indicies: {idx1} {idx2}")
#     model = instance_to_model(fp, detail=True)
#     assert isinstance(model, SiibraTabularModel)
#     assert model.data
#     model.dict()


# bb_query = WagstylBigBrainProfileQuery()
# bb_pr_features = bb_query.features

# cell_pr_features = [f for f in REGISTRY[CellDensityProfile]]
# receptor_pr_features = [f for f in REGISTRY[ReceptorDensityProfile]]

# all_pr_features = [
#     *bb_pr_features[:10],
#     *cell_pr_features[:10],
#     *receptor_pr_features[:10],
# ] if os.environ.get("FAST_RUN") else [
#     *bb_pr_features,
#     *cell_pr_features,
#     *receptor_pr_features,
# ]

# @pytest.mark.parametrize('pr', all_pr_features)
# def test_pr(pr: CorticalProfile):
#     assert isinstance(pr, CorticalProfile)
#     model = instance_to_model(pr)
#     assert isinstance(model, CorticalProfileModel)
#     model.dict()

# random_five_pr_features = get_random_n(5, [
#     bb_pr_features,
#     cell_pr_features,
#     receptor_pr_features,
# ])

# @pytest.mark.parametrize('pr', random_five_pr_features)
# def test_pr_detail(pr: CorticalProfile):
#     model = instance_to_model(pr, detail=True)
#     assert isinstance(model, CorticalProfileModel)
#     assert model.data
#     model.dict()

