import json
import mock

from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app)


def test_get_all_gene_names():
    response = client.get('/v1_0/genes')
    assert response.status_code == 200
    result_content = json.loads(response.content)
    assert len(result_content['genes']) > 0


def test_get_all_available_modalities():
    response = client.get('/v1_0/modalities')
    assert response.status_code == 200
    result_content = json.loads(response.content)
    assert len(result_content) > 0


# def test_raise_exception_on_receptor_distribution_for_wrong_region():
#     response = client.get(
#         '/v1_0/features/ReceptorDistribution?region=dummy',
#         headers={"Authorization": "Bearer token"}
#     )
#     assert response.status_code == 404
#
#
# def test_raise_exception_for_wrong_receptor_distribution():
#     response = client.get(
#         '/v1_0/features/WrongDistribution?region=dummy',
#         headers={"Authorization": "Bearer token"}
#     )
#     assert response.status_code == 422
#
#
# def test_get_connectivity_profile():
#     response = client.get(
#         '/v1_0/features/ConnectivityProfile?region=dummy',
#         headers={"Authorization": "Bearer token"}
#     )
#     assert response.status_code == 501
#
#
# def test_get_connectivity_matrix():
#     response = client.get(
#         '/v1_0/features/ConnectivityMatrix?region=dummy',
#         headers={"Authorization": "Bearer token"}
#     )
#     assert response.status_code == 501

