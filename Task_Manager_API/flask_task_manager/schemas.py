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


# i think  i neeed to separate this , USer must have some flexibility here , for updating any field  int he  task
class AddTask(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    completion = fields.Boolean(required=False)

    @validates_schema
    def validate_identifier(self, data, **kwargs):
        if data.get("title") == "" and data.get("description") == "":
            raise ValidationError("title and  description cant be empty")


class UpdateTask(Schema):
    title = fields.Str(required=False)
    description = fields.Str(required=False)
    completion = fields.Boolean(required=False)

    @validates_schema
    def validate_identifier(self, data, **kwargs):
        if data.get("title") == "" and data.get("description") == "":
            raise ValidationError("title and  description cant be empty")


class ForgetPassword(Schema):
    email = fields.Email(required=True)


class VerifyOtp(Schema):
    otp = fields.Str(required=True)
    email = fields.Email(required=True)


class ResetPassword(Schema):
    new_password = fields.Str(required=True, validate=validate.Length(min=8))
