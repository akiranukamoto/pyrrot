import json
import os
import re
import uuid
from http import HTTPStatus

import yaml
from apispec import APISpec
from flask import Flask, jsonify, request
from flask_apispec import FlaskApiSpec, doc, use_kwargs, marshal_with

from schema import ConfigSchema


def _comparisons(path):
    def _compare_simple_dict(config, request):
        if len(config.items()) == len(request.items()):
            for k, v in config.items():
                if isinstance(v, dict):
                    return _compare_simple_dict(v, request[k])
                else:
                    if (str(v).startswith('$regex=') and not re.match(v[7:].replace("\\", "\\\\"),
                                                                      str(request[k]))) or (
                                not str(v).startswith('$regex=') and v != request[k]):
                        return False
            return True
        return False

    def _compare_path(config, request):
        if config and str(config).startswith('$regex='):
            return re.match(config[7:].replace("\\", "\\\\"), request)
        return config is None or request == config

    def _compare_method(config, request):
        return request == config

    def _compare_headers(config, request):
        request_upper = {k.upper(): v for k, v in request.items()}
        for k, v in config.items():
            if (str(v).startswith('$regex=') and not re.match(v[7:].replace("\\", "\\\\"), request_upper[k])) or (
                        not str(v).startswith('$regex=') and v != request_upper[k]):
                return False
        return True

    def _compare_type(config, request):
        return request == config

    def _compare_body(config, request):
        return _compare_simple_dict(config, request)

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
    return jsonify(then.get('body')), then.get('code'), then.get('header')


def get_request(app, path=''):
    selected_config = list(filter(_comparisons(path), app.config['PYRROT_CONFIG']))[0]
    selected_config['then']['header']['call_count'] = app.config['PYRROT_CALL_COUNT'][selected_config['id']] + 1
    app.config['PYRROT_CALL_COUNT'][selected_config['id']] = app.config['PYRROT_CALL_COUNT'][selected_config['id']] + 1
    return _build_response(selected_config)


def find_config_by_id(configs, id):
    for config in configs:
        if str(id) == config['id']:
            return config


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


def _read_configs(app, path):
    configs = []
    app.config['PYRROT_CALL_COUNT'] = {}

    if os.path.isfile(path):
        configs = _load_config(path)
    elif os.path.isdir(path):
        for file in os.listdir(path):
            if file.endswith(".yaml") or file.endswith(".yml"):
                configs += _load_config(os.path.join(path, file))
    for config in configs:
        config['id'] = str(uuid.uuid4())
        app.config['PYRROT_CALL_COUNT'][config['id']] = 0
    app.config['PYRROT_CONFIG'] = configs
    return configs


def _add_url_rules(app):
    @app.route('/', methods=METHODS)
    def get_request_without_path():
        return get_request(app)

    @app.route('/<path:path>', methods=METHODS)
    def get_request_with_path(path):
        return get_request(app, path)

    @app.route('/pyrrot', methods=['POST'])
    @doc(tags=['configuration'], description='Insert new endpoint.')
    @use_kwargs(ConfigSchema)
    @marshal_with(ConfigSchema)
    def post_config(**kwargs):
        kwargs['id'] = str(uuid.uuid4())
        app.config['PYRROT_CALL_COUNT'][kwargs['id']] = 0
        app.config['PYRROT_CONFIG'].append(kwargs)
        return kwargs, HTTPStatus.CREATED

    @app.route('/pyrrot/<uuid:id>', methods=['DELETE'])
    @doc(tags=['configuration'], description='Delete endpoint.')
    def delete_config(id):
        config = find_config_by_id(app.config['PYRROT_CONFIG'], id)
        if config:
            app.config['PYRROT_CONFIG'].remove(config)
            return '', HTTPStatus.OK
        return '', HTTPStatus.NOT_FOUND

    @app.route('/pyrrot', methods=['GET'])
    @doc(tags=['configuration'], description='Get all endpoints.')
    @marshal_with(ConfigSchema(many=True))
    def get_all_config():
        return app.config['PYRROT_CONFIG']

    @app.route('/pyrrot/<uuid:id>', methods=['GET'])
    @doc(tags=['configuration'], description='Get endpoint by id.')
    @marshal_with(ConfigSchema)
    def get_by_id_config(id):
        config = find_config_by_id(app.config['PYRROT_CONFIG'], id)
        if config:
            return config
        return '', HTTPStatus.NOT_FOUND

    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='Pyrrot Apis',
            version='v1',
            plugins=['apispec.ext.marshmallow'],
        ),
        'APISPEC_SWAGGER_URL': '/swagger/',
    })
    docs = FlaskApiSpec(app)
    docs.register(post_config)
    docs.register(delete_config)
    docs.register(get_all_config)
    docs.register(get_by_id_config)


def _register_exceptions(app):
    @app.errorhandler(Exception)
    def exception(_):
        response = jsonify({'message': 'URL NOT FOUND'})
        response.status_code = HTTPStatus.NOT_FOUND
        return response


if __name__ == "__main__":
    examples = os.path.dirname(__file__)
    app = create_app(debug=True)
    _read_configs(app, os.path.join(examples, "examples"))
    app.run(port=1234)
