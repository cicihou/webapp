# -*- coding: utf-8 -*-

from flask import Blueprint, request, abort

from webapp.utils import pure_jsonify

bp_main = Blueprint('main', __name__, url_prefix=None)


@bp_main.route('/healthz', methods=['GET'])
def index():
    return pure_jsonify()
