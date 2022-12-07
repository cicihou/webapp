# -*- coding: utf-8 -*-
import json
import logging
import os
import time
from os.path import splitext, join
from urllib.parse import quote

import boto3
from botocore.exceptions import ClientError
from flask import Blueprint, request, abort, g, current_app
from werkzeug.utils import secure_filename

from permissions import login_required, check_user_auth
from schema import AccountCreateSchema, validate_schema, AccountUpdateSchema, AccountVerifySchema
from webapp.config import CONF
from webapp.models import Account, Document
from webapp.utils import pure_jsonify, status_jsonify, hash_pw, now, random_string, ok_jsonify, fail_jsonify

bp_main = Blueprint('main', __name__, url_prefix=None)
logger = logging.getLogger(__name__)


@bp_main.route('/healthz', methods=['GET'])
def index():
    return pure_jsonify()


@bp_main.route('/v1/verifyUserEmail', methods=['GET'])
@validate_schema(AccountVerifySchema)
def verify_account():
    kwarg = g.json_params
    acc = Account.query.filter_by(username=kwarg['email']).first_or_404()
    if acc.verified:
        return ok_jsonify('account already verified')
    resp = DynamoClient().read(kwarg['email'], kwarg['token'])
    if resp:
        acc.verified = 1
        acc.update()
    else:
        return fail_jsonify('ttl invalid or info wrong')
    return ok_jsonify('account verified')


@bp_main.route('/v2/account/<id>', methods=['GET'])
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
    token = random_string()
    DynamoClient().create(account.username, token)
    SNSClient().post_sns_msg(f'{CONF.APP_URL}/v1/verifyUserEmail?email={account.username}&token={token}', account.username)
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
    S3Client().delete_file(doc_id)
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
    doc = Document.query.filter_by(user_id=user.id, doc_id=doc_id).first_or_404()
    return pure_jsonify([doc.to_dict()])


def _create_resource():
    doc, file = get_resource()
    user = Account.query.filter_by(username=g.username, password=g.password).first()
    if not user:
        abort(401)
    doc['user_id'] = user.id
    doc = Document(**doc)
    doc.save()
    doc.s3_bucket_path += doc.doc_id
    doc.update()
    S3Client().upload_file(file, CONF.S3_BUCKET, doc.doc_id, doc.to_dict())
    return doc


def get_resource():
    file = request.files.get('file', None)
    fileType = request.files.get('fileType', None)

    if not file or file.filename == '':
        return abort(400)
    fileType = fileType or splitext(file.filename)[1].lower()[1:]
    filename = secure_filename(quote(file.filename))
    doc = dict(name=filename, s3_bucket_path=f'https://{CONF.S3_BUCKET}.s3.amazonaws.com/')
    return doc, file


class S3Client:
    def __init__(self):
        self.s3 = boto3.client("s3")

    def upload_file(self, file_name, bucket, object_name=None, metadata={}):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)
        try:
            response = self.s3.upload_fileobj(file_name, bucket, object_name,
                                                ExtraArgs={'Metadata': metadata})
            logging.info(response)
        except ClientError as e:
            logging.error(e)

    def delete_file(self, doc_id):
        self.s3.delete_object(Bucket=CONF.S3_BUCKET, Key=doc_id)


class SNSClient:
    def __init__(self):
        self.sns_client = boto3.client('sns', region_name=CONF.REGION)

    def post_sns_msg(self, verify_link, useremail):
        resp = self.sns_client.publish(TopicArn=CONF.SNS_TOPIC_ARN,
                       Message=json.dumps(dict(content=f"Click on {verify_link} to verify your account",
                                               to=useremail)),
                       Subject="Verify your account")
        logger.info(resp)


class DynamoClient:
    def __init__(self, table=CONF.DYNAMO_TABLE, ttl=int(CONF.DYNAMO_TTL), region=CONF.REGION):
        self.client = boto3.resource('dynamodb', region_name=region)
        self.table = self.client.Table(table)
        self.ttl = ttl
        self.cur = int(time.time())

    def create(self, username, token):
        try:
            resp = self.table.put_item(Item={'username': username, 'token': token, 'tokenttl': self.cur + self.ttl})
            logger.info(resp)
        except Exception as e:
            logger.info({f"Dynamo put fail, {str(e)}"})

    def read(self, username, token):
        try:
            resp = self.table.get_item(Key={'username': username, 'token': token})
            item = resp.get('Item', {})
        except ClientError as e:
            logger.info({f"Dynamo read fail, {e.response['Error']['Message']}"})
        else:
            return item and item['username'] == username and self.cur <= item['tokenttl']
