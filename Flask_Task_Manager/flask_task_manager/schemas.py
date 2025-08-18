from marshmallow import schemas, fields, ValidationError


class UserSchema(schemas):
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)


class AddTask(schemas):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
