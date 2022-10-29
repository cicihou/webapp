# -*- coding: utf-8 -*-
import functools
import logging
import os
from os.path import splitext, join
from urllib.parse import quote

import boto3
from botocore.exceptions import ClientError
from flask import Blueprint, request, abort, g, current_app
from werkzeug.utils import secure_filename

from permissions import login_required, check_user_auth
from schema import AccountCreateSchema, validate_schema, AccountUpdateSchema
from webapp.config import CONF
from webapp.models import Account, Document
from webapp.utils import pure_jsonify, status_jsonify, hash_pw, now

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


@bp_main.route('/v1/documents', methods=['POST'])
@login_required
def create_document():
    """ create document to s3"""
    doc = _create_resource()
    return pure_jsonify(doc.to_dict())


@bp_main.route('/v1/documents/<doc_id>', methods=['DELETE'])
@login_required
def delete_document(doc_id):
    user = Account.query.filter_by(username=g.username, password=g.password).first()
    if not user:
        abort(401)
    doc = Document.query.filter_by(user_id=user.id, doc_id=doc_id).first_or_404()
    doc.delete()
    delete_file(doc_id)
    return pure_jsonify(), 204


@bp_main.route('/v1/documents/', methods=['GET'])
@login_required
def read_documents():
    user = Account.query.filter_by(username=g.username, password=g.password).first()
    if not user:
        abort(403)
    docs = Document.query.filter_by(user_id=user.id).all()
    data = [doc.to_dict() for doc in docs]
    return pure_jsonify(data)


@bp_main.route('/v1/documents/<doc_id>', methods=['GET'])
@login_required
def read_document(doc_id):
    user = Account.query.filter_by(username=g.username, password=g.password).first()
    if not user:
        abort(403)
    doc = Document.query.filter_by(user_id=user.id, doc_id=doc_id).first()
    return pure_jsonify([doc.to_dict()])


def _create_resource():
    doc, file = get_resource()
    user = Account.query.filter_by(username=g.username, password=g.password).first()
    if not user:
        abort(401)
    doc['user_id'] = user.id
    doc = Document(**doc)
    doc.save()
    upload_file(file, CONF.S3_BUCKET, doc.doc_id, doc.to_dict())
    return doc


def get_resource():
    file = request.files.get('file', None)
    fileType = request.files.get('fileType', None)

    if not file or file.filename == '':
        return abort(400)
    fileType = fileType or splitext(file.filename)[1].lower()[1:]
    filename = secure_filename(quote(file.filename))
    doc = dict(name=filename, s3_bucket_path=CONF.S3_BUCKET)
    return doc, file


def upload_file(file_name, bucket, object_name=None, metadata={}):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_fileobj(file_name, bucket, object_name,
                                            ExtraArgs={'Metadata': metadata})
        logging.info(response)
    except ClientError as e:
        logging.error(e)


def delete_file(doc_id):
    s3 = boto3.client("s3")
    s3.delete_object(Bucket=CONF.S3_BUCKET, Key=doc_id)
