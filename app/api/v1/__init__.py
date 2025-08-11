#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API v1 模块
"""

from flask import Blueprint

# 创建 API v1 蓝图
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api')

# 导入所有路由模块
from . import workflows
from . import node_types
from . import executions
from . import files
from . import system