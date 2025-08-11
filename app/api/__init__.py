#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API蓝图模块
"""

from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from . import routes