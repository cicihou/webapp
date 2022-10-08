import json
import re
import urllib.parse
import uuid

from sqlalchemy import Column, Integer, SmallInteger, String, Text, DateTime, Boolean
from sqlalchemy import TypeDecorator, ForeignKey, inspect
from sqlalchemy.orm import relationship, backref

from webapp.config import CONF
from webapp.extensions import db
from webapp.utils import utcnow, now, json_dumps, random_string, camelcase_to_underscore, utcISOnow
from webapp.utils.encrypt import aes


class EncryptedType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        return aes.encrypt(value)

    def process_result_value(self, value, dialect):
        return aes.decrypt(value)


class JSONType(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        return json_dumps(value)

    def process_result_value(self, value, dialect):
        if not value:
            return value
        return json.loads(value)


class ModelMixin(object):
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update_dict(self, values, allowed_fields=None):
        if not allowed_fields:
            columns = values.keys()
        else:
            columns = set(allowed_fields) & set(values.keys())
        for col in columns:
            setattr(self, col, values[col])

    def null(self, txt):
        if txt == '':
            return None
        return txt

    def to_dict(self):
        res = {}
        for k in self._dict_fields:
            res[k] = getattr(self, k)
        return res


class TimestampMixin(object):
    created_at = Column(DateTime, default=now, nullable=False)
    updated_at = Column(DateTime, default=now, onupdate=now, nullable=False)


class Account(db.Model, ModelMixin):
    __tablename__ = 'accounts'
    _dict_fields = ('id', 'first_name', 'last_name', 'username', 'account_created', 'account_updated')

    id = Column(String(64), primary_key=True, default=str(uuid.uuid4()))
    first_name = Column(String(64))
    last_name = Column(String(64))
    password = Column(String(256))
    username = Column(String(256))  # email
    account_created = Column(String(256), default=utcISOnow, nullable=False)
    account_updated = Column(String(256), default=utcISOnow, onupdate=utcISOnow, nullable=False)

    def __repr__(self):
        return '<MyModel(id={})>'.format(self.id)
