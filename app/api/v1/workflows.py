#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API v1 工作流管理路由
"""

from flask import request, jsonify, g
from functools import wraps
import logging

from . import api_v1
from app.services.workflow_service import WorkflowService
from app.database import db

logger = logging.getLogger(__name__)

def require_auth(f):
    """认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 这里应该实现实际的认证逻辑
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

@api_v1.route('/workflows', methods=['GET'])
def get_workflows():
    """获取工作流列表"""
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        category = request.args.get('category')
        status = request.args.get('status')
        
        service = WorkflowService(db.session)
        result = service.get_workflows(
            page=page,
            size=size,
            category=category,
            status=status
        )
        
        return jsonify(success_response(result))
        
    except Exception as e:
        logger.error(f"Error in get_workflows: {str(e)}")
        return jsonify(error_response('获取工作流列表失败', 500)), 500

@api_v1.route('/workflows', methods=['POST'])
@require_auth
def create_workflow():
    """创建工作流"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(error_response('请求数据不能为空')), 400
        
        service = WorkflowService(db.session)
        result = service.create_workflow(data, g.user_id)
        
        return jsonify(success_response(result, '创建工作流成功')), 201
        
    except ValueError as e:
        return jsonify(error_response(str(e))), 400
    except Exception as e:
        logger.error(f"Error in create_workflow: {str(e)}")
        return jsonify(error_response('创建工作流失败', 500)), 500

@api_v1.route('/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    """获取工作流详情"""
    try:
        user_id = getattr(g, 'user_id', None)
        
        service = WorkflowService(db.session)
        result = service.get_workflow_detail(workflow_id, user_id)
        
        return jsonify(success_response(result))
        
    except ValueError as e:
        return jsonify(error_response(str(e), 404)), 404
    except Exception as e:
        logger.error(f"Error in get_workflow: {str(e)}")
        return jsonify(error_response('获取工作流详情失败', 500)), 500

@api_v1.route('/workflows/<workflow_id>', methods=['PUT'])
@require_auth
def update_workflow(workflow_id):
    """更新工作流"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(error_response('请求数据不能为空')), 400
        
        service = WorkflowService(db.session)
        result = service.update_workflow(workflow_id, data, g.user_id)
        
        return jsonify(success_response(result, '更新工作流成功'))
        
    except ValueError as e:
        return jsonify(error_response(str(e))), 400
    except Exception as e:
        logger.error(f"Error in update_workflow: {str(e)}")
        return jsonify(error_response('更新工作流失败', 500)), 500

@api_v1.route('/workflows/<workflow_id>', methods=['DELETE'])
@require_auth
def delete_workflow(workflow_id):
    """删除工作流"""
    try:
        service = WorkflowService(db.session)
        service.delete_workflow(workflow_id, g.user_id)
        
        return jsonify(success_response(None, '删除工作流成功'))
        
    except ValueError as e:
        return jsonify(error_response(str(e))), 400
    except Exception as e:
        logger.error(f"Error in delete_workflow: {str(e)}")
        return jsonify(error_response('删除工作流失败', 500)), 500

@api_v1.route('/workflows/<workflow_id>/publish', methods=['POST'])
@require_auth
def publish_workflow(workflow_id):
    """发布工作流"""
    try:
        service = WorkflowService(db.session)
        result = service.publish_workflow(workflow_id, g.user_id)
        
        return jsonify(success_response(result, '发布工作流成功'))
        
    except ValueError as e:
        return jsonify(error_response(str(e))), 400
    except Exception as e:
        logger.error(f"Error in publish_workflow: {str(e)}")
        return jsonify(error_response('发布工作流失败', 500)), 500

@api_v1.route('/workflows/<workflow_id>/test', methods=['POST'])
@require_auth
def test_workflow(workflow_id):
    """测试工作流"""
    try:
        data = request.get_json() or {}
        
        service = WorkflowService(db.session)
        result = service.test_workflow(workflow_id, g.user_id, data)
        
        return jsonify(success_response(result, '测试工作流成功'))
        
    except ValueError as e:
        return jsonify(error_response(str(e))), 400
    except Exception as e:
        logger.error(f"Error in test_workflow: {str(e)}")
        return jsonify(error_response('测试工作流失败', 500)), 500

@api_v1.route('/workflows/<workflow_id>/execute', methods=['POST'])
@require_auth
def execute_workflow(workflow_id):
    """执行工作流"""
    try:
        data = request.get_json() or {}
        
        service = WorkflowService(db.session)
        result = service.execute_workflow(workflow_id, g.user_id, data)
        
        return jsonify(success_response(result, '执行工作流成功'))
        
    except ValueError as e:
        return jsonify(error_response(str(e))), 400
    except Exception as e:
        logger.error(f"Error in execute_workflow: {str(e)}")
        return jsonify(error_response('执行工作流失败', 500)), 500