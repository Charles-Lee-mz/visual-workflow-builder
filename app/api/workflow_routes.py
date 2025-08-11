#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流API路由
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
import logging

from app.services.workflow_service import WorkflowService
from app.database import db
from app.models.workflow import WorkflowCategory

logger = logging.getLogger(__name__)

# 创建工作流蓝图
workflow_bp = Blueprint('workflow', __name__)

def get_current_user():
    """获取当前用户ID（可选）"""
    return getattr(g, 'user_id', None)

def require_auth(f):
    """认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 这里应该实现实际的认证逻辑
        # 例如检查JWT token等
        if not hasattr(g, 'user_id'):
            return jsonify({
                'success': False,
                'error': '需要登录'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

@workflow_bp.route('', methods=['GET'])
def search_workflows():
    """搜索工作流"""
    try:
        # 获取查询参数
        query = request.args.get('q', '')
        category = request.args.get('category')
        tags = request.args.get('tags', '').split(',') if request.args.get('tags') else []
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        
        # 调用服务层
        service = WorkflowService(db.session)
        result = service.search_workflows(
            query=query,
            category=category,
            tags=tags,
            sort_by=sort_by,
            order=order,
            page=page,
            size=size
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in search_workflows: {str(e)}")
        return jsonify({
            'success': False,
            'error': '搜索工作流失败'
        }), 500

@workflow_bp.route('', methods=['POST'])
@require_auth
def create_workflow():
    """创建工作流"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必需字段
        required_fields = ['name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        service = WorkflowService(db.session)
        result = service.create_workflow(data, g.user_id)
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error in create_workflow: {str(e)}")
        return jsonify({
            'success': False,
            'error': '创建工作流失败'
        }), 500

@workflow_bp.route('/<workflow_id>', methods=['GET'])
def get_workflow_detail(workflow_id):
    """获取工作流详情"""
    try:
        user_id = get_current_user()  # 可选的用户ID
        
        service = WorkflowService(db.session)
        result = service.get_workflow_detail(workflow_id, user_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error in get_workflow_detail: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取工作流详情失败'
        }), 500

@workflow_bp.route('/<workflow_id>', methods=['PUT'])
@require_auth
def update_workflow(workflow_id):
    """更新工作流"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = WorkflowService(db.session)
        result = service.update_workflow(workflow_id, data, g.user_id)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error in update_workflow: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新工作流失败'
        }), 500

@workflow_bp.route('/<workflow_id>', methods=['DELETE'])
@require_auth
def delete_workflow(workflow_id):
    """删除工作流"""
    try:
        service = WorkflowService(db.session)
        result = service.delete_workflow(workflow_id, g.user_id)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error in delete_workflow: {str(e)}")
        return jsonify({
            'success': False,
            'error': '删除工作流失败'
        }), 500

@workflow_bp.route('/<workflow_id>/fork', methods=['POST'])
@require_auth
def fork_workflow(workflow_id):
    """复制工作流"""
    try:
        service = WorkflowService(db.session)
        result = service.fork_workflow(workflow_id, g.user_id)
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error in fork_workflow: {str(e)}")
        return jsonify({
            'success': False,
            'error': '复制工作流失败'
        }), 500

@workflow_bp.route('/<workflow_id>/publish', methods=['POST'])
@require_auth
def publish_workflow(workflow_id):
    """发布工作流"""
    try:
        service = WorkflowService(db.session)
        result = service.publish_workflow(workflow_id, g.user_id)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error in publish_workflow: {str(e)}")
        return jsonify({
            'success': False,
            'error': '发布工作流失败'
        }), 500

@workflow_bp.route('/<workflow_id>/reviews', methods=['POST'])
@require_auth
def rate_workflow(workflow_id):
    """评价工作流"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not rating:
            return jsonify({'error': '评分不能为空'}), 400
        
        service = WorkflowService(db.session)
        result = service.rate_workflow(workflow_id, g.user_id, rating, comment)
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error in rate_workflow: {str(e)}")
        return jsonify({
            'success': False,
            'error': '评价工作流失败'
        }), 500

@workflow_bp.route('/trending', methods=['GET'])
def get_trending_workflows():
    """获取热门工作流"""
    try:
        category = request.args.get('category')
        time_range = request.args.get('time_range', '7d')
        limit = int(request.args.get('limit', 20))
        
        service = WorkflowService(db.session)
        result = service.get_trending_workflows(category, time_range, limit)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in get_trending_workflows: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取热门工作流失败'
        }), 500

@workflow_bp.route('/my', methods=['GET'])
@require_auth
def get_my_workflows():
    """获取我的工作流"""
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        
        service = WorkflowService(db.session)
        result = service.get_user_workflows(g.user_id, page, size)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in get_my_workflows: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取我的工作流失败'
        }), 500

@workflow_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取工作流分类"""
    try:
        categories = [{
            'value': category.value,
            'label': category.value.replace('_', ' ').title()
        } for category in WorkflowCategory]
        
        return jsonify({
            'success': True,
            'data': categories
        })
        
    except Exception as e:
        logger.error(f"Error in get_categories: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取分类失败'
        }), 500

@workflow_bp.route('/stats', methods=['GET'])
def get_marketplace_stats():
    """获取工作流广场统计信息"""
    try:
        # 统计信息查询
        
        # 这里可以添加统计查询逻辑
        # 例如：总工作流数、活跃用户数、热门分类等
        
        stats = {
            'total_workflows': 0,
            'total_users': 0,
            'total_forks': 0,
            'popular_categories': []
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error in get_marketplace_stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取统计信息失败'
        }), 500

# 错误处理
@workflow_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': '资源不存在'
    }), 404

@workflow_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500