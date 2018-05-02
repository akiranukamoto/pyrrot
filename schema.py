from http import HTTPStatus

from marshmallow import Schema, fields
from marshmallow.validate import OneOf

METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'PATCH', 'TRACE', 'OPTIONS']


class WhenConfigSchema(Schema):
    path = fields.String(required=True)
    method = fields.String(default='GET', validate=OneOf(METHODS))
    type = fields.String(default='application/json', validate=OneOf(['application/json']))
    header = fields.Dict()
    body = fields.Dict()
    query = fields.Dict()


class ThenConfigSchema(Schema):
    method = fields.String(default='GET', validate=OneOf(METHODS))
    type = fields.String(default='application/json', validate=OneOf(['application/json']))
    header = fields.Dict()
    body = fields.Dict()
    code = fields.Int(default=HTTPStatus.OK, validate=OneOf(list(map(int, HTTPStatus))))


class ConfigSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    when = fields.Nested(WhenConfigSchema, required=False)
    then = fields.Nested(ThenConfigSchema, required=False)
