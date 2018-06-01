from http import HTTPStatus

from flask import jsonify

from .comparison import comparisons
from .constant import CALL_COUNT_PARAM, CONFIG_PARAM
from .schema import METHODS


def register_rules(app):
    def _build_response(value):
        then = value.get('then')
        return jsonify(then.get('body')), then.get('code'), then.get('header')

    @app.route('/', methods=METHODS)
    def get_request_without_path():
        return ""

    @app.route('/<path:path>', methods=METHODS)
    def get_request_with_path(path):
        selected_config = list(filter(comparisons(path), app.config[CONFIG_PARAM]))[0]
        selected_config['then']['header']['call_count'] = app.config[CALL_COUNT_PARAM][selected_config['id']] + 1
        app.config[CALL_COUNT_PARAM][selected_config['id']] = app.config[CALL_COUNT_PARAM][selected_config['id']] + 1
        return _build_response(selected_config)


def register_exceptions(app):
    @app.errorhandler(Exception)
    def exception(_):
        response = jsonify({'message': 'URL NOT FOUND'})
        response.status_code = HTTPStatus.NOT_FOUND
        return response
