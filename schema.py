import functools

from flask import request, g, abort
from marshmallow import INCLUDE, EXCLUDE, Schema, fields, validates_schema, post_load

from webapp.utils import hash_pw, status_jsonify


class AccountMxin:
    first_name = fields.String(required=True, allow_none=False)
    last_name = fields.String(required=True, allow_none=False)
    password = fields.String(required=True, allow_none=False)


class AccountCreateSchema(Schema, AccountMxin):
    _allow_params = ('username', 'first_name', 'last_name', 'password')
    username = fields.Email(required=True, allow_none=False)

    @post_load
    def process(self, item, **kwargs):
        item = {k : item[k] for k in item if k in self._allow_params}
        return item

    @validates_schema
    def validate_email_address(self, data, *args, **kwargs):
        email = data.get('username')
        from webapp.models import Account
        account = Account.query.filter_by(username=email).first()
        if account:
            print('dup email')
            abort(400)


class AccountUpdateSchema(Schema, AccountMxin):
    _allow_params = ('first_name', 'last_name', 'password')

    @post_load
    def process(self, item, **kwargs):
        item['password'] = hash_pw(item['password'].encode())
        return item

    @validates_schema
    def validate_fields(self, data, *args, **kwargs):
        for key in data:
            if key not in self._allow_params:
                # {'msg': 'only first_name, last_name, password are allowed'}
                abort(400)


def validate_schema(schema):
    def wrapper(view_func):
        @functools.wraps(view_func)
        def f(*args, **kwargs):
            if request.method in ['POST', 'PUT']:
                params = request.get_json()
            else:
                params = request.args.to_dict()
            try:
                data = schema(unknown=INCLUDE).load(params)
            except Exception as e:
                abort(400)
            g.json_params = data
            return view_func(*args, **kwargs)

        return f

    return wrapper
