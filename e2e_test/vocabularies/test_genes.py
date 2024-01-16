import pytest
from fastapi.testclient import TestClient
from api.server import api

client = TestClient(api)

@pytest.mark.parametrize('find, expect_no', [
    (None, 50),
    ("MA", 50),
    ("MAO", 2),
    ("MAOC", 0),
])
def test_genes(find, expect_no):
    response = client.get(f"/v3_0/vocabularies/genes", params={
        "find": find
    })
    assert response.status_code == 200
    resp_json = response.json()
    items = resp_json.get("items", [])
    
    assert len(items) == expect_no
    