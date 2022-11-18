import base64
import functools

from flask import abort, request, g

from webapp.models import Account
from webapp.utils import hash_pw


def login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):

        token = validate_token()
        if not token:
            abort(401)
        if not is_verified():
            abort(401)
        return view_func(*args, **kwargs)

    return wrapper


def validate_token():
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
    try:
        token = base64.b64decode(token).decode('ascii')
    except:
        return
    username, pw = token.split(':')
    password = hash_pw(pw.encode())
    g.raw_password = pw
    g.username = username
    g.password = password
    return parts[1]


def is_verified():
    acc = Account.query.filter_by(username=g.username).first_or_404()
    return acc.verified


def check_user_auth(id):
    acc = Account.query.filter_by(username=g.username, password=g.password).first()
    if not acc or acc.id != id:
        abort(403)
