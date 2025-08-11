#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API v1 系统管理路由
"""

from flask import jsonify
import logging

from . import api_v1
from app.services.system_service import SystemService
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

@api_v1.route('/system/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        service = SystemService(db.session)
        result = service.health_check()
        
        return jsonify(success_response(result))
        
    except Exception as e:
        logger.error(f"Error in health_check: {str(e)}")
        return jsonify(error_response('健康检查失败', 500)), 500

@api_v1.route('/system/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    try:
        service = SystemService(db.session)
        result = service.get_system_info()
        
        return jsonify(success_response(result))
        
    except Exception as e:
        logger.error(f"Error in get_system_info: {str(e)}")
        return jsonify(error_response('获取系统信息失败', 500)), 500