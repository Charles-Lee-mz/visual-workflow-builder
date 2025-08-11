#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型使用统计和调用日志模型
"""

from datetime import datetime
from app.database import db

class ModelUsage(db.Model):
    """模型使用统计模型"""
    __tablename__ = 'model_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    model_config_id = db.Column(db.Integer, db.ForeignKey('model_configs.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    total_calls = db.Column(db.Integer, default=0)  # 总调用次数
    total_tokens = db.Column(db.Integer, default=0)  # 总token消耗
    success_calls = db.Column(db.Integer, default=0)  # 成功调用次数
    failed_calls = db.Column(db.Integer, default=0)  # 失败调用次数
    last_called_at = db.Column(db.DateTime)  # 最后调用时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    model_config = db.relationship('ModelConfig', backref=db.backref('usage_stats', lazy=True))
    user = db.relationship('User', backref=db.backref('model_usage', lazy=True))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'model_config_id': self.model_config_id,
            'user_id': self.user_id,
            'total_calls': self.total_calls,
            'total_tokens': self.total_tokens,
            'success_calls': self.success_calls,
            'failed_calls': self.failed_calls,
            'success_rate': round(self.success_calls / max(self.total_calls, 1) * 100, 2),
            'last_called_at': self.last_called_at.isoformat() if self.last_called_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ModelUsage {self.model_config_id} - {self.total_calls} calls>'

# ModelCallLog 已在 model_call_log.py 中定义，避免重复定义