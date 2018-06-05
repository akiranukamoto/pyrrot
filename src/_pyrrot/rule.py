import json
from http import HTTPStatus

from flask import jsonify, render_template

from .comparison import comparisons
from .constant import CALL_COUNT_PARAM, CONFIG_PARAM
from .schema import METHODS


def register_rules(app):
    def _build_template(configurations):
        response = []
        for config in configurations:
            response.append({'id': config['id'],
                             'name': config['name'],
                             'call_count': app.config[CALL_COUNT_PARAM][config['id']],
                             'code': json.dumps(config, indent=4, sort_keys=True)})
        return response

    def _build_response(value):
        then = value.get('then')
        return jsonify(then.get('body')), then.get('code'), then.get('header')

    @app.route('/', methods=METHODS)
    def get_request_without_path():
        return render_template('config.html', configurations=_build_template(app.config[CONFIG_PARAM]))

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
        print(_)
        return response
