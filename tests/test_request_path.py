import pytest
from flask import json


def test_with_paths(client, url_example_path):
    response = client(url_example_path).get('/users', content_type='application/json')
    data = json.loads(response.get_data(as_text=True))
    assert 200 == response.status_code
    assert 'abc123456' == response.headers['TRACKID']
    assert 'John Doe' == data['name']
    assert 666 == data['identity']


@pytest.mark.parametrize('path', ['/users/wrong', '/fruta/abacaxi', '/test?foo=bar', '/jaca'])
def test_with_wrong_paths(client, url_example_path, path):
    response = client(url_example_path).get(path, content_type='application/json')
    assert 404 == response.status_code
    json_response = json.loads(response.get_data(as_text=True))
    assert not json_response['get_users_path']['path']
    assert not json_response['get_companies_path']['path']
