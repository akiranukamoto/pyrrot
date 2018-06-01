import json
import re

from flask import request


def comparisons(path):
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
        try:
            return _compare_path(when.get('path'), path) \
                   and _compare_method(when.get('method'), request.method) \
                   and _compare_headers(when.get('header') or {}, dict(request.headers.items())) \
                   and _compare_type(when.get('type'), request.content_type) \
                   and _compare_body(when.get('body') or {}, json.loads(request.data.decode('utf8') or '{}')) \
                   and _compare_query(when.get('query') or {}, request.args.to_dict())
        except:
            return False

    return compare
