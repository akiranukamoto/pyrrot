import rstr

from .comparison import RegexBase


class ResponseBuilder(RegexBase):
    def __init__(self, body):
        self._body = body
        self._type = type(self._body)

    def generate(self):
        if self._body is not None:
            self._body = [self._body] if self._type is dict else self._body
            for i, data in enumerate(self._body):
                self._body[i] = self._create_body(self._body[i])

            return self._extract_body(self._body)
        return None

    def _create_body(self, data: dict):
        for k, v in data.items():
            if self._is_regex(v):
                data[k] = self._generate_by_regex(v)
        return data

    @staticmethod
    def _generate_by_regex(value):
        return rstr.xeger(value[7:])

    def _extract_body(self, body):
        if self._type is dict:
            return body[0]
        return body
