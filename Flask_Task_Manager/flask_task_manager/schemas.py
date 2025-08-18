from marshmallow import Schema, fields, ValidationError


class UserSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)


class AddTask(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
