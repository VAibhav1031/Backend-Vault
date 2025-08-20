from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))


class LoginSchema(Schema):
    username = fields.Str(required=False)
    email = fields.Email(required=False)
    password = fields.Str(required=True)

    @validates_schema
    def validate_identifier(self, data, **kwargs):
        if not data.get("username") and not data.get("email"):
            raise ValidationError("Either email or username is required")


class AddTask(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
