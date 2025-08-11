#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API v1 文件管理路由
"""

from flask import request, jsonify, g
from functools import wraps
import logging

from . import api_v1
from app.services.file_service import FileService
from app.database import db

logger = logging.getLogger(__name__)

def require_auth(f):
    """认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user_id'):
            return jsonify({
                'code': 401,
                'message': '需要登录',
                'data': None
            }), 401
        return f(*args, **kwargs)
    return decorated_function

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

@api_v1.route('/files/upload', methods=['POST'])
@require_auth
def upload_file():
    """上传文件"""
    try:
        if 'file' not in request.files:
            return jsonify(error_response('没有文件')), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify(error_response('文件名不能为空')), 400
        
        service = FileService(db.session)
        result = service.upload_file(file, g.user_id)
        
        return jsonify(success_response(result, '上传文件成功'))
        
    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}")
        return jsonify(error_response('上传文件失败', 500)), 500

@api_v1.route('/files/<file_id>', methods=['GET'])
@require_auth
def get_file(file_id):
    """获取文件信息"""
    try:
        service = FileService(db.session)
        result = service.get_file_info(file_id, g.user_id)
        
        return jsonify(success_response(result))
        
    except ValueError as e:
        return jsonify(error_response(str(e), 404)), 404
    except Exception as e:
        logger.error(f"Error in get_file: {str(e)}")
        return jsonify(error_response('获取文件信息失败', 500)), 500

@api_v1.route('/files/<file_id>', methods=['DELETE'])
@require_auth
def delete_file(file_id):
    """删除文件"""
    try:
        service = FileService(db.session)
        service.delete_file(file_id, g.user_id)
        
        return jsonify(success_response(None, '删除文件成功'))
        
    except ValueError as e:
        return jsonify(error_response(str(e))), 400
    except Exception as e:
        logger.error(f"Error in delete_file: {str(e)}")
        return jsonify(error_response('删除文件失败', 500)), 500