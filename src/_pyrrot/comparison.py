import json
import re

from flask import request

from .constant import REGEX_PARAM


def comparisons(path):
    def _is_regex(value):
        return str(value).startswith(REGEX_PARAM)

    def _match_regex(regex, value):
        return re.match(regex[7:].replace("\\", "\\\\"), str(value))

    def _compare_simple_dict(config, _request):
        if len(config.items()) == len(_request.items()):
            for k, v in config.items():
                if isinstance(v, dict):
                    return _compare_simple_dict(v, _request[k])
                else:
                    if (_is_regex(v) and not _match_regex(v, _request[k])) or (not _is_regex(v) and v != _request[k]):
                        return False
            return True
        return False

    def _compare_path(config, _request):
        if config and _is_regex(config):
            return _match_regex(config, _request)
        return config is None or config == _request

    def _compare_method(config, _request):
        return config == _request

    def _compare_headers(config, _request):
        request_upper = {k.upper(): v for k, v in _request.items()}
        for k, v in config.items():
            if (_is_regex(v) and not _match_regex(v, request_upper[k])) or (not _is_regex(v) and v != request_upper[k]):
                return False
        return True

    def _compare_type(config, _request):
        return config == _request

    def _compare_body(config, _request):
        return _compare_simple_dict(config, _request)

    def _compare_query(config, _request):
        return _compare_simple_dict(config, _request)

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
