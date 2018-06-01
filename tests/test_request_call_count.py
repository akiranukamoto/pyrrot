import pytest

from src._pyrrot import main
from src._pyrrot.config import read_configs


@pytest.fixture
def client(url_example_example):
    app = main.create_app(debug=True)
    main.configs = read_configs(app, url_example_example)
    yield app.test_client()


@pytest.mark.parametrize('count', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
def test_call_count(client, count):
    for _ in range(count):
        response = client.get('/users?foo=bar', headers={'TRACKID': 'abc123456'}, content_type='application/json')
    assert str(count) == dict(response.headers)['call_count']
