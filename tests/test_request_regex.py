import pytest
from flask import json


@pytest.mark.parametrize("path, header, body",
                         [("/special_customers", "simple_access", {'name': 'coca cola', 'identity': 3}),
                          ("/customers_is_special", "access_foo", {'name': 'Pepsi Cola', 'identity': 8}),
                          ("/before_customers_after", "simple_access_bar", {'name': 'Cola', 'identity': 10}),
                          ("/profile/123/accounts/123", "simple_access_bar", {'name': 'Cola', 'identity': 10})
                          ])
def test_with_regex(client, url_example_regex, path, header, body):
    response = client(url_example_regex).post(path, data=json.dumps(body),
                                              headers={'TRACKID': header},
                                              content_type='application/json')
    data = json.loads(response.get_data(as_text=True))
    assert 201 == response.status_code
    assert 'abc123456' == response.headers['TRACKID']
    assert 'Coca Cola' == data['name']
    assert 1234567 == data['identity']


@pytest.mark.parametrize("query",
                         ['fruta=laranja', 'fruta=laranja_lima', 'fruta=foo_laranja'])
def test_with_query_regex(client, url_example_regex, query):
    response = client(url_example_regex).get('/customers?{}'.format(query), content_type='application/json')
    data = json.loads(response.get_data(as_text=True))
    assert 200 == response.status_code
    assert 'abc123456' == response.headers['TRACKID']
    assert 'Coca Cola' == data['name']
    assert 1234567 == data['identity']


@pytest.mark.parametrize("path, header, body",
                         [("/special_customer", "simple_access", {'name': 'coca cola', 'identity': 3}),  # wrong path
                          ("/user", "access_foo", {'name': 'Pepsi Cola', 'identity': 8}),  # wrong path
                          ("/customers", "token", {'name': 'Cola', 'identity': 10}),  # wrong header
                          ("/customers", "access_foo", {'name': 'Fanta', 'identity': 10}),  # wrong body
                          ("/special_customers", "simple_access", {'name': None, 'identity': 3}),  # wrong body
                          ("/special_customers", "simple_access", {'name': 'coca cola', 'identity': 100})  # wrong body
                          ])
def test_with_wrong_regex(client, url_example_regex, path, header, body):
    response = client(url_example_regex).post(path, data=json.dumps(body),
                                              headers={'TRACKID': header},
                                              content_type='application/json')
    assert 404 == response.status_code
