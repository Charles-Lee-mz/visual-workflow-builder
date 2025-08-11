#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API v1 执行管理路由
"""

from flask import request, jsonify, g
from functools import wraps
import logging

from . import api_v1
from app.services.execution_service import ExecutionService
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

@api_v1.route('/executions', methods=['GET'])
@require_auth
def get_executions():
    """获取执行记录列表"""
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        workflow_id = request.args.get('workflow_id')
        status = request.args.get('status')
        
        service = ExecutionService(db.session)
        result = service.get_executions(
            user_id=g.user_id,
            page=page,
            size=size,
            workflow_id=workflow_id,
            status=status
        )
        
        return jsonify(success_response(result))
        
    except Exception as e:
        logger.error(f"Error in get_executions: {str(e)}")
        return jsonify(error_response('获取执行记录失败', 500)), 500

@api_v1.route('/executions/<execution_id>', methods=['GET'])
@require_auth
def get_execution(execution_id):
    """获取执行详情"""
    try:
        service = ExecutionService(db.session)
        result = service.get_execution_detail(execution_id, g.user_id)
        
        return jsonify(success_response(result))
        
    except ValueError as e:
        return jsonify(error_response(str(e), 404)), 404
    except Exception as e:
        logger.error(f"Error in get_execution: {str(e)}")
        return jsonify(error_response('获取执行详情失败', 500)), 500

@api_v1.route('/executions/<execution_id>/status', methods=['GET'])
@require_auth
def get_execution_status(execution_id):
    """获取执行状态"""
    try:
        service = ExecutionService(db.session)
        result = service.get_execution_status(execution_id, g.user_id)
        
        return jsonify(success_response(result))
        
    except ValueError as e:
        return jsonify(error_response(str(e), 404)), 404
    except Exception as e:
        logger.error(f"Error in get_execution_status: {str(e)}")
        return jsonify(error_response('获取执行状态失败', 500)), 500

@api_v1.route('/executions/<execution_id>/cancel', methods=['POST'])
@require_auth
def cancel_execution(execution_id):
    """取消执行"""
    try:
        service = ExecutionService(db.session)
        result = service.cancel_execution(execution_id, g.user_id)
        
        return jsonify(success_response(result, '取消执行成功'))
        
    except ValueError as e:
        return jsonify(error_response(str(e))), 400
    except Exception as e:
        logger.error(f"Error in cancel_execution: {str(e)}")
        return jsonify(error_response('取消执行失败', 500)), 500

@api_v1.route('/executions/stats', methods=['GET'])
@require_auth
def get_execution_stats():
    """获取执行统计"""
    try:
        time_range = request.args.get('time_range', '7d')
        
        service = ExecutionService(db.session)
        result = service.get_execution_stats(g.user_id, time_range)
        
        return jsonify(success_response(result))
        
    except Exception as e:
        logger.error(f"Error in get_execution_stats: {str(e)}")
        return jsonify(error_response('获取执行统计失败', 500)), 500