from marshmallow import Schema, fields


class PostSchema(Schema):
    id = fields.Int(dump_only=True)
    content = fields.Str(load_only=True, required=True)
    title = fields.Str(load_only=True, required=True)

class AuthorLoginSchema(Schema):
    # id = fields.Int(dump_only=True)
    username = fields.Str(load_only=True, required=True)
    password = fields.Str(load_only=True, required=True)

class AuthorApprove(Schema):
    first_name = fields.Str(load_only=True, required=True)
    last_name = fields.Str(load_only=True, required=True)
    cityzen_id = fields.Str(load_only=True, required=True)

class ProjectClose(Schema):
    helper = fields.Bool(load_only=True, reuqired=True)
