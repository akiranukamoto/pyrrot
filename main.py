import json
import os
from http import HTTPStatus

import yaml
from flask import Flask, jsonify, request

from schema import ConfigSchema

configs = []


def _comparisons(path):
    def _compare_simple_dict(config, request):
        return sorted(config.items()) == sorted(request.items())

    def _compare_path(config, request):
        return config is None or '/{}'.format(request) == config

    def _compare_method(config, request):
        return request == config

    def _compare_headers(config, request):
        request_upper = {k.upper(): v for k, v in request.items()}
        return len(config) == len(set(config.items()) & set(request_upper.items()))

    def _compare_type(config, request):
        return request == config

    def _compare_body(config, request):
        teste = _compare_simple_dict(config, request)
        return teste

    def _compare_query(config, request):
        return _compare_simple_dict(config, request)

    def compare(value):
        when = value.get('when', {})
        return _compare_path(when.get('path'), path) \
               and _compare_method(when.get('method'), request.method) \
               and _compare_headers(when.get('header') or {}, dict(request.headers.items())) \
               and _compare_type(when.get('type'), request.content_type) \
               and _compare_body(when.get('body') or {}, json.loads(request.data.decode('utf8') or '{}')) \
               and _compare_query(when.get('query') or {}, request.args.to_dict())

    return compare


def _build_response(value):
    then = value.get('then')
    then.get('header')['call_count'] = then.get('header', {}).get('call_count', 0) + 1
    return jsonify(then.get('body')), then.get('code'), then.get('header')


def get_request(path=''):
    return _build_response(list(filter(_comparisons(path), configs))[0])


METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'PATCH', 'TRACE', 'OPTIONS']


def create_app(debug=False):
    app = Flask(__name__)
    app.debug = debug
    _add_url_rules(app)
    _register_exceptions(app)
    return app


def _load_config(file):
    with open(file, 'r') as stream:
        try:
            config, error = ConfigSchema(many=True).load(yaml.load(stream))
            if error:
                raise RuntimeError(error)
            return config
        except yaml.YAMLError as exc:
            raise RuntimeError(exc)


def _read_configs(path):
    configs = []
    index = 0
    if os.path.isfile(path):
        configs = _load_config(path)
    elif os.path.isdir(path):
        for file in os.listdir(path):
            if file.endswith(".yaml") or file.endswith(".yml"):
                configs += _load_config(os.path.join(path, file))
    for config in configs:
        index += 1
        config['index'] = index
    return configs


def _add_url_rules(app):
    app.add_url_rule('/', '', get_request, methods=METHODS)
    app.add_url_rule('/<path:path>', '', get_request, methods=METHODS)


def _register_exceptions(app):
    @app.errorhandler(Exception)
    def exception(_):
        response = jsonify({'message': 'URL NOT FOUND'})
        response.status_code = HTTPStatus.NOT_FOUND
        return response


if __name__ == "__main__":
    examples = os.path.dirname(__file__)
    configs = _read_configs(os.path.join(examples, "examples"))
    app = create_app(debug=True)
    app.run(port=1234)
