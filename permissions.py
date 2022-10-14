import base64
import functools

from flask import abort, request

from webapp.models import Account
from webapp.utils import hash_pw


def login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):

        token = get_access_token()
        if not token:
            abort(401)
        return view_func(*args, **kwargs)

    return wrapper


def get_access_token():
    """ Authorization -> access_token"""
    auth_header = request.headers.get('Authorization')
    token = ''
    if not auth_header:
        return token

    parts = auth_header.split(' ')
    if len(parts) != 2:
        return token
    if parts[0].lower() != 'basic':
        return token
    token = parts[1]
    return token


def check_user_auth(id):
    token = get_access_token()
    try:
        token = base64.b64decode(token).decode('ascii')
    except:
        abort(401)
    username, pw = token.split(':')
    password = hash_pw(pw.encode())
    acc = Account.query.filter_by(username=username, password=password).first()
    if not acc or acc.id != id:
        abort(403)
