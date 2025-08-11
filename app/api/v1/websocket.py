#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket实时通信模块
"""

from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
import logging
from datetime import datetime
import json
from functools import wraps

from app.database import db
from app.models.workflow_execution import WorkflowExecution
from app.models.workflow_execution import NodeExecution

logger = logging.getLogger(__name__)

# 全局SocketIO实例（需要在应用初始化时设置）
socketio = None

def init_socketio(app):
    """初始化SocketIO"""
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode='threading',
        logger=True,
        engineio_logger=True
    )
    
    # 注册事件处理器
    register_handlers()
    
    return socketio

def get_current_user():
    """获取当前用户ID（简化版本）"""
    return request.headers.get('X-User-ID', 'anonymous')

def require_auth(f):
    """需要认证的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_current_user()
        if not user_id or user_id == 'anonymous':
            emit('error', {
                'code': 401,
                'message': '未授权访问',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
            disconnect()
            return
        return f(*args, **kwargs)
    return decorated_function

def register_handlers():
    """注册WebSocket事件处理器"""
    
    @socketio.on('connect')
    def handle_connect():
        """客户端连接事件"""
        user_id = get_current_user()
        logger.info(f"Client connected: {request.sid}, user: {user_id}")
        
        emit('connected', {
            'message': '连接成功',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """客户端断开连接事件"""
        user_id = get_current_user()
        logger.info(f"Client disconnected: {request.sid}, user: {user_id}")
    
    @socketio.on('join_execution')
    def handle_join_execution(data):
        """加入执行监听房间"""
        try:
            execution_id = data.get('execution_id')
            if not execution_id:
                emit('error', {
                    'code': 400,
                    'message': '缺少execution_id参数',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                })
                return
            
            # 验证执行记录是否存在
            execution = WorkflowExecution.query.filter_by(id=execution_id).first()
            if not execution:
                emit('error', {
                    'code': 404,
                    'message': '执行记录不存在',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                })
                return
            
            # 加入房间
            room_name = f"execution_{execution_id}"
            join_room(room_name)
            
            logger.info(f"Client {request.sid} joined execution room: {room_name}")
            
            # 发送当前执行状态
            emit('execution_status', {
                'type': 'execution_status',
                'data': {
                    'execution_id': execution.id,
                    'status': execution.status,
                    'started_at': execution.started_at.isoformat() + 'Z',
                    'completed_at': execution.completed_at.isoformat() + 'Z' if execution.completed_at else None,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            })
            
        except Exception as e:
            logger.error(f"Error in join_execution: {str(e)}")
            emit('error', {
                'code': 500,
                'message': '加入监听失败',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
    
    @socketio.on('leave_execution')
    def handle_leave_execution(data):
        """离开执行监听房间"""
        try:
            execution_id = data.get('execution_id')
            if not execution_id:
                emit('error', {
                    'code': 400,
                    'message': '缺少execution_id参数',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                })
                return
            
            room_name = f"execution_{execution_id}"
            leave_room(room_name)
            
            logger.info(f"Client {request.sid} left execution room: {room_name}")
            
            emit('left_execution', {
                'execution_id': execution_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
            
        except Exception as e:
            logger.error(f"Error in leave_execution: {str(e)}")
            emit('error', {
                'code': 500,
                'message': '离开监听失败',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
    
    @socketio.on('get_execution_status')
    def handle_get_execution_status(data):
        """获取执行状态"""
        try:
            execution_id = data.get('execution_id')
            if not execution_id:
                emit('error', {
                    'code': 400,
                    'message': '缺少execution_id参数',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                })
                return
            
            execution = WorkflowExecution.query.filter_by(id=execution_id).first()
            if not execution:
                emit('error', {
                    'code': 404,
                    'message': '执行记录不存在',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                })
                return
            
            # 获取节点执行进度
            node_executions = NodeExecution.query.filter_by(execution_id=execution.id).all()
            total_nodes = len(node_executions)
            completed_nodes = len([ne for ne in node_executions if ne.status in ['success', 'failed']])
            
            # 获取当前正在执行的节点
            current_node = None
            running_node = next((ne for ne in node_executions if ne.status == 'running'), None)
            if running_node:
                current_node = running_node.node_id
            
            # 计算进度百分比
            percentage = int((completed_nodes / total_nodes * 100)) if total_nodes > 0 else 0
            
            emit('execution_status', {
                'type': 'execution_status',
                'data': {
                    'execution_id': execution.id,
                    'status': execution.status,
                    'progress': {
                        'total_nodes': total_nodes,
                        'completed_nodes': completed_nodes,
                        'current_node': current_node,
                        'percentage': percentage
                    },
                    'started_at': execution.started_at.isoformat() + 'Z',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            })
            
        except Exception as e:
            logger.error(f"Error in get_execution_status: {str(e)}")
            emit('error', {
                'code': 500,
                'message': '获取执行状态失败',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })

def broadcast_execution_status(execution_id, status, current_node=None, progress=None):
    """广播执行状态更新"""
    if not socketio:
        return
    
    try:
        room_name = f"execution_{execution_id}"
        
        message_data = {
            'type': 'execution_status',
            'data': {
                'execution_id': execution_id,
                'status': status,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }
        
        if current_node:
            message_data['data']['current_node'] = current_node
        
        if progress:
            message_data['data']['progress'] = progress
        
        socketio.emit('execution_status', message_data, room=room_name)
        logger.info(f"Broadcasted execution status to room {room_name}: {status}")
        
    except Exception as e:
        logger.error(f"Error broadcasting execution status: {str(e)}")

def broadcast_node_completed(execution_id, node_id, status, output_data=None, duration_ms=None):
    """广播节点执行完成"""
    if not socketio:
        return
    
    try:
        room_name = f"execution_{execution_id}"
        
        message_data = {
            'type': 'node_completed',
            'data': {
                'execution_id': execution_id,
                'node_id': node_id,
                'status': status,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }
        
        if output_data is not None:
            message_data['data']['output_data'] = output_data
        
        if duration_ms is not None:
            message_data['data']['duration_ms'] = duration_ms
        
        socketio.emit('node_completed', message_data, room=room_name)
        logger.info(f"Broadcasted node completion to room {room_name}: {node_id} - {status}")
        
    except Exception as e:
        logger.error(f"Error broadcasting node completion: {str(e)}")

def broadcast_execution_completed(execution_id, status, output_data=None, duration_ms=None):
    """广播执行完成"""
    if not socketio:
        return
    
    try:
        room_name = f"execution_{execution_id}"
        
        message_data = {
            'type': 'execution_completed',
            'data': {
                'execution_id': execution_id,
                'status': status,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }
        
        if output_data is not None:
            message_data['data']['output_data'] = output_data
        
        if duration_ms is not None:
            message_data['data']['duration_ms'] = duration_ms
        
        socketio.emit('execution_completed', message_data, room=room_name)
        logger.info(f"Broadcasted execution completion to room {room_name}: {status}")
        
    except Exception as e:
        logger.error(f"Error broadcasting execution completion: {str(e)}")

def broadcast_error(execution_id, error_message, node_id=None):
    """广播错误信息"""
    if not socketio:
        return
    
    try:
        room_name = f"execution_{execution_id}"
        
        message_data = {
            'type': 'execution_error',
            'data': {
                'execution_id': execution_id,
                'error_message': error_message,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }
        
        if node_id:
            message_data['data']['node_id'] = node_id
        
        socketio.emit('execution_error', message_data, room=room_name)
        logger.info(f"Broadcasted error to room {room_name}: {error_message}")
        
    except Exception as e:
        logger.error(f"Error broadcasting error: {str(e)}")

# 导出函数供其他模块使用
__all__ = [
    'init_socketio',
    'broadcast_execution_status',
    'broadcast_node_completed', 
    'broadcast_execution_completed',
    'broadcast_error'
]