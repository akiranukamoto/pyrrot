import pytest
from flask import json


def test_with_queries(client, url_example_query):
    response = client(url_example_query).get('/users?foo=bar&fruta=abacaxi',
                                             content_type='application/json')
    data = json.loads(response.get_data(as_text=True))
    assert 200 == response.status_code
    assert 'abc123456' == response.headers['TRACKID']
    assert 'John Doe' == data['name']
    assert 666 == data['identity']


def test_without_queries(client, url_example_query):
    response = client(url_example_query).get('/companies', content_type='application/json')
    data = json.loads(response.get_data(as_text=True))
    assert 200 == response.status_code
    assert 'abc123456' == response.headers['TRACKID']
    assert 'Oracle' == data['name']
    assert 999 == data['identity']


@pytest.mark.parametrize('query', ['?fruta=abacaxi', '?foo=bar&fruta=jaca', ''])
def test_with_wrong_queries(client, url_example_query, query):
    response = client(url_example_query).get('/users{}'.format(query), content_type='application/json')
    assert 404 == response.status_code
    json_response = json.loads(response.get_data(as_text=True))
    assert not json_response['get_users_query']['query']