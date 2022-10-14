# -*- coding: utf-8 -*-

from flask import Blueprint, request, abort, g

from permissions import login_required, check_user_auth
from schema import AccountCreateSchema, validate_schema, AccountUpdateSchema
from webapp.models import Account
from webapp.utils import pure_jsonify, status_jsonify, hash_pw

bp_main = Blueprint('main', __name__, url_prefix=None)


@bp_main.route('/healthz', methods=['GET'])
def index():
    return pure_jsonify()


@bp_main.route('/v1/account/<id>', methods=['GET'])
@login_required
def read_account(id):
    check_user_auth(id)
    account = Account.query.get_or_404(id)
    return pure_jsonify(account.to_dict())


@bp_main.route('/v1/account/<id>', methods=['PUT'])
@validate_schema(AccountUpdateSchema)
@login_required
def update_account(id):
    check_user_auth(id)
    account = Account.query.get_or_404(id)
    account.update_dict(g.json_params, allowed_fields=['first_name', 'last_name', 'password'])
    account.save()
    return pure_jsonify(), 204


@bp_main.route('/v1/account', methods=['POST'])
@validate_schema(AccountCreateSchema)
def create_account():
    kwarg = g.json_params
    auth = kwarg['username'] + ':' + kwarg['password']
    kwarg['password'] = hash_pw(kwarg['password'].encode())
    account = Account(**kwarg)
    account.save()
    return status_jsonify(201, account.to_dict(), auth)
