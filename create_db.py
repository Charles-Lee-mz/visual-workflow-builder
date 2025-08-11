#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库创建脚本
"""

from app import create_app
from app.database import db

# 导入所有模型
from app.models.user import User
from app.models.intent import Intent
from app.models.execution import Execution
from app.models.model_config import ModelConfig
from app.models.model_usage import ModelUsage
from app.models.workflow import Workflow, WorkflowReview, WorkflowStats

def create_database():
    """创建数据库表"""
    app = create_app()
    
    with app.app_context():
        # 删除所有表
        db.drop_all()
        print("已删除所有表")
        
        # 创建所有表
        db.create_all()
        print("已创建所有表")
        
        # 验证表是否创建成功
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"创建的表: {tables}")
        
        # 检查model_configs表的列
        if 'model_configs' in tables:
            columns = inspector.get_columns('model_configs')
            print(f"model_configs表的列: {[col['name'] for col in columns]}")
        
if __name__ == '__main__':
    create_database()