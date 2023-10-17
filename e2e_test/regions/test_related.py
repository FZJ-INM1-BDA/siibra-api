import pytest
from fastapi.testclient import TestClient
from api.server import api

client = TestClient(api)

@pytest.mark.parametrize("parc, reg_spec, has_related, has_homology", [
    ("2.9", "PGa", True, True),
    ("monkey", "PG", False, True),
    ("waxholm v3", "cornu ammonis 1", True, False),
])
def test_related(parc, reg_spec, has_related, has_homology):
    response = client.get(f"/v3_0/regions/{reg_spec}/related", params={
        "parcellation_id": parc
    })
    assert response.status_code == 200
    resp_json = response.json()
    items = resp_json.get("items", [])
    
    other_versions = [item for item in items if item.get("qualification") == "OTHER_VERSION"]
    homologous = [item for item in items if item.get("qualification") == "HOMOLOGOUS"]
    assert (len(other_versions) > 0) == has_related
    assert (len(homologous) > 0) == has_homology
