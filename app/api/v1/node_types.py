#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API v1 节点类型路由
"""

from flask import jsonify
import logging

from . import api_v1
from app.services.node_service import NodeService
from app.database import db

logger = logging.getLogger(__name__)

def success_response(data=None, message='操作成功'):
    """成功响应格式"""
    return {
        'code': 200,
        'message': message,
        'data': data
    }

def error_response(message='操作失败', code=400):
    """错误响应格式"""
    return {
        'code': code,
        'message': message,
        'data': None
    }

@api_v1.route('/node-types', methods=['GET'])
def get_node_types():
    """获取节点类型列表"""
    try:
        service = NodeService(db.session)
        result = service.get_node_types()
        
        return jsonify(success_response(result))
        
    except Exception as e:
        logger.error(f"Error in get_node_types: {str(e)}")
        return jsonify(error_response('获取节点类型失败', 500)), 500

@api_v1.route('/node-types/<type_id>', methods=['GET'])
def get_node_type(type_id):
    """获取节点类型详情"""
    try:
        service = NodeService(db.session)
        result = service.get_node_type_detail(type_id)
        
        return jsonify(success_response(result))
        
    except ValueError as e:
        return jsonify(error_response(str(e), 404)), 404
    except Exception as e:
        logger.error(f"Error in get_node_type: {str(e)}")
        return jsonify(error_response('获取节点类型详情失败', 500)), 500