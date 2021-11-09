from .util import Session
import os
import pytest

base_url=os.getenv('SIIBRA_API_E2E_BASE_URL', 'http://localhost:5000')
client = Session(base_url=base_url)

paths = [
    {
        'path': '/',
        'contains': 'Siibra'
    },
    {
        'path': '/stats',
        'contains': 'Siibra - statistics'
    }
]

ci_flag = os.environ.get('SIIBRA_CI')

@pytest.mark.skipif(ci_flag, reason=f'In CI, TestClient does not run Templates properly.')
@pytest.mark.parametrize('path_obj', paths)
def test_try_html(path_obj):
    response = client.get(path_obj.get('path'))
    assert response.status_code == 200
    assert path_obj.get('contains') in str(response.content)
