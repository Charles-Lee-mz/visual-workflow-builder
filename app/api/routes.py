#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由
"""

from flask import jsonify, request
from . import api_bp
from app.models import User, Intent, Execution, ModelConfig
from app.database import db

@api_bp.route('/users', methods=['GET'])
def get_users():
    """获取用户列表"""
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users],
        'total': len(users)
    })

@api_bp.route('/intents', methods=['GET'])
def get_intents():
    """获取意图列表"""
    intents = Intent.query.all()
    return jsonify({
        'intents': [intent.to_dict() for intent in intents],
        'total': len(intents)
    })

@api_bp.route('/executions', methods=['GET'])
def get_executions():
    """获取执行列表"""
    executions = Execution.query.all()
    return jsonify({
        'executions': [execution.to_dict() for execution in executions],
        'total': len(executions)
    })

@api_bp.route('/model-configs', methods=['GET'])
def get_model_configs():
    """获取模型配置列表"""
    configs = ModelConfig.query.all()
    return jsonify({
        'model_configs': [config.to_dict() for config in configs],
        'total': len(configs)
    })

@api_bp.route('/chat', methods=['POST'])
def chat():
    """聊天接口"""
    data = request.get_json()
    message = data.get('message', '')
    
    # 简单的回复逻辑
    response = {
        'message': f'收到您的消息: {message}',
        'timestamp': request.environ.get('REQUEST_TIME', 'unknown')
    }
    
    return jsonify(response)