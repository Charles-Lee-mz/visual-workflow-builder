#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用启动脚本
"""

from app import create_app
from app.database import db
from app.models import *  # 导入所有模型

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """为Flask shell提供上下文"""
    return {
        'db': db,
        'app': app
    }

if __name__ == '__main__':
    import os
    
    with app.app_context():
        # 创建数据库表
        db.create_all()
        print("数据库表已创建")
    
    # 获取端口号，默认使用5001
    port = int(os.environ.get('PORT', 5001))
    
    # 启动应用（包含WebSocket支持）
    if hasattr(app, 'socketio'):
        app.socketio.run(app, debug=True, host='0.0.0.0', port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port)