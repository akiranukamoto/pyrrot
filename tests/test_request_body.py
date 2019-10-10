import pytest
from flask import json


def test_with_body(client, url_example_body):
    response = client(url_example_body).post('/users', data=json.dumps({
        'name': 'John Doe', 'identity': 666, 'address': {
            'number': 321,
            'street': 'White River'
        }}), content_type='application/json')
    data = json.loads(response.get_data(as_text=True))
    assert 201 == response.status_code
    assert 'abc123456' == response.headers['TRACKID']
    assert 'John Doe' == data['name']
    assert 666 == data['identity']


def test_without_body(client, url_example_body):
    response = client(url_example_body).get('/companies', content_type='application/json')
    assert 200 == response.status_code
    assert 'abc123456' == response.headers['TRACKID']


def test_without_body_with_post(client, url_example_body):
    response = client(url_example_body).post('/companies', data=json.dumps({
        'name': 'John Doe', 'identity': 666, 'address': {
            'number': 321,
            'street': 'White River'
        }}), content_type='application/json')
    assert 200 == response.status_code
    json_response = json.loads(response.get_data(as_text=True))
    assert [{'ticket': '1234'}, {'ticket': '5678'}] == json_response


@pytest.mark.parametrize('body', [json.dumps({'name': 'John Doe', 'identity': 999}),
                                  json.dumps({'name': 'John Doe'}),
                                  None])
def test_with_wrong_body(client, url_example_body, body):
    response = client(url_example_body).post('/users', data=body,
                                             content_type='application/json')
    assert 404 == response.status_code
    json_response = json.loads(response.get_data(as_text=True))
    assert not json_response['insert_users_body']['body']


def test_array_body(client, url_example_body):
    response = client(url_example_body).get('/tickets', content_type='application/json')
    assert 200 == response.status_code
    json_response = json.loads(response.get_data(as_text=True))
    assert 2 == len(json_response)
    assert [{'ticket': '1234'}, {'ticket': '5678'}] == json_response
