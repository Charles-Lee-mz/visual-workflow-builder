#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用工厂
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from .database import db, migrate, init_db
from config import Config

# 创建扩展实例
cors = CORS()
jwt = JWTManager()

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 设置JSON编码
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'
    
    # 配置日志记录
    if app.debug:
        logging.basicConfig(level=logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
    
    # 初始化扩展
    init_db(app)
    cors.init_app(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:3001', 'http://127.0.0.1:3001'], supports_credentials=True)
    jwt.init_app(app)
    
    # 初始化WebSocket
    from app.api.v1.websocket import init_socketio
    socketio = init_socketio(app)
    
    # 导入模型（避免循环导入）
    from app.models import user, intent, execution, model_config, model_usage, workflow
    
    # 注册蓝图
    from app.main import main_bp
    from app.api import api_bp
    from app.intent import intent_bp
    from app.models_api import models_api_bp
    from app.api.workflow_routes import workflow_bp
    from app.api.v1 import api_v1
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(intent_bp, url_prefix='/api/intent')
    app.register_blueprint(models_api_bp, url_prefix='/api/models')
    app.register_blueprint(workflow_bp, url_prefix='/api/workflows')
    app.register_blueprint(api_v1)  # API v1 已经包含了 /api 前缀
    
    # 将socketio实例附加到app，以便其他模块可以访问
    app.socketio = socketio
    
    return app