import base64
import datetime
import decimal
import json
import re

import bcrypt
import shortuuid
from flask import jsonify, make_response
from sqlalchemy.orm.query import Query

from webapp.config import CONF


def utcnow():
    return datetime.datetime.utcnow()


def now():
    return datetime.datetime.now()


def utcISOnow():
    ''' example: 2016-08-29T09:12:33.001Z '''
    return datetime.datetime.utcnow().isoformat()[:-3] + 'Z'


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoding class, to handle Decimal and datetime.date instances."""

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)

        if isinstance(o, datetime.date):
            return o.isoformat()

        if isinstance(o, datetime.timedelta):
            return str(o)

        if isinstance(o, Query):
            return list(o)

        super(JSONEncoder, self).default(o)


def json_dumps(data, **kwargs):
    return json.dumps(data, cls=JSONEncoder, **kwargs)


def pretty_print(v):
    print(json_dumps(v, indent=2, ensure_ascii=False))


def generate_auth(txt):
    return "Basic " + base64.b64encode(txt.encode('ascii')).decode('ascii')


def pure_jsonify(data={}):
    return jsonify(data)


def status_jsonify(status_code, data={}, auth=''):
    rsp = make_response(jsonify(data), status_code)
    if auth:
        rsp.headers["Authorization"] = generate_auth(auth)
    return rsp


def ok_jsonify(data=None):
    return jsonify({'ok': True, 'data': data if data is not None else {}})


def fail_jsonify(reason, data=None):
    return jsonify({'ok': True, 'data': data if data is not None else {}, 'reason': reason})


def validate_email(address):
    return re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", address) is not None


def safe_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError) as e:
        return default


def pager(query, model, orderby='', page=1, count=100):
    """
    :type query: flask_sqlalchemy.BaseQuery
    :type model: flask_sqlalchemy.Model
    :param orderby: asc '+field', 'field'，desc '-field'
    :type orderby: str
    :param page: offset
    :type page: int
    :param count: limit
    :type count: int
    """
    total = query.count()

    if orderby:
        order_field = orderby.lstrip('+-')
        field = getattr(model, order_field, None)
        if field is None or not hasattr(field, 'asc'):
            field = model.id

        if orderby.startswith('-'):
            query = query.order_by(field.desc())
        else:
            query = query.order_by(field.asc())

    page = max(1, page)
    rows = query.offset((page - 1) * count).limit(count).all()
    return rows, total


def camelcase_to_underscore(s):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def random_string(length=10):
    return shortuuid.random(length)


def hash_pw(pw, salt=CONF.BCRYPT_SALT):
    hashed = bcrypt.hashpw(pw, salt)
    return hashed
