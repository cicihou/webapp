# -*- coding: utf-8 -*-

from flask import Blueprint, request, abort, g

from permissions import login_required, check_user_auth
from schema import AccountCreateSchema, validate_schema, AccountUpdateSchema
from webapp.models import Account
from webapp.utils import pure_jsonify, auth_jsonify

bp_main = Blueprint('main', __name__, url_prefix=None)


@bp_main.route('/healthz', methods=['GET'])
def index():
    return pure_jsonify()


@bp_main.route('/account/<id>', methods=['GET'])
@login_required
def read_account(id):
    check_user_auth(id)
    account = Account.query.get_or_404(id)
    return pure_jsonify(account.to_dict())


@bp_main.route('/account/<id>', methods=['PUT'])
@validate_schema(AccountUpdateSchema)
@login_required
def update_account(id):
    check_user_auth(id)
    account = Account.query.get_or_404(id)
    if not account:
        abort(204)
    account.update_dict(g.json_params, allowed_fields=['first_name', 'last_name', 'password'])
    account.save()
    return pure_jsonify(), 204


@bp_main.route('/account', methods=['POST'])
@validate_schema(AccountCreateSchema)
def create_account():
    kwarg = g.json_params
    account = Account(**kwarg)
    account.save()
    txt = account.username + ':' + account.password
    return auth_jsonify(txt, account.to_dict())
