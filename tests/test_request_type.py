import json


def test_wrong_method(client, url_example_example):
    response = client(url_example_example).get('/users?foo=bar', headers={'TRACKID': 'abc123456'},
                                         content_type='application/text')
    assert 404 == response.status_code
    json_response = json.loads(response.get_data(as_text=True))
    assert not json_response['get_users']['type']
