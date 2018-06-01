from http import HTTPStatus

from flask import jsonify

from .comparison import comparisons

METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'PATCH', 'TRACE', 'OPTIONS']


def register_rules(app):
    def _build_response(value):
        then = value.get('then')
        return jsonify(then.get('body')), then.get('code'), then.get('header')

    @app.route('/', methods=METHODS)
    def get_request_without_path():
        return ""

    @app.route('/<path:path>', methods=METHODS)
    def get_request_with_path(path):
        selected_config = list(filter(comparisons(path), app.config['PYRROT_CONFIG']))[0]
        selected_config['then']['header']['call_count'] = app.config['PYRROT_CALL_COUNT'][selected_config['id']] + 1
        app.config['PYRROT_CALL_COUNT'][selected_config['id']] = app.config['PYRROT_CALL_COUNT'][
                                                                     selected_config['id']] + 1
        return _build_response(selected_config)


def register_exceptions(app):
    @app.errorhandler(Exception)
    def exception(_):
        response = jsonify({'message': 'URL NOT FOUND'})
        response.status_code = HTTPStatus.NOT_FOUND
        return response
