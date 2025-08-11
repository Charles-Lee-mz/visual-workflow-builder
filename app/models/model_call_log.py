#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型调用日志模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import db

class ModelCallLog(db.Model):
    """模型调用日志"""
    
    __tablename__ = 'model_call_logs'
    
    id = Column(Integer, primary_key=True, comment='日志ID')
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, comment='用户ID')
    model_config_id = Column(Integer, ForeignKey('model_configs.id'), nullable=True, comment='模型配置ID')
    
    # 模型信息
    provider = Column(String(50), nullable=False, comment='模型提供商')
    model_name = Column(String(100), nullable=False, comment='模型名称')
    
    # 调用信息
    request_data = Column(Text, comment='请求数据')
    response_data = Column(Text, comment='响应数据')
    
    # 统计信息
    prompt_tokens = Column(Integer, default=0, comment='输入token数')
    completion_tokens = Column(Integer, default=0, comment='输出token数')
    total_tokens = Column(Integer, default=0, comment='总token数')
    
    # 性能信息
    response_time = Column(Float, comment='响应时间(秒)')
    
    # 状态信息
    is_success = Column(Boolean, default=True, comment='是否成功')
    error_message = Column(Text, comment='错误信息')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关联关系
    user = relationship('User', backref='model_call_logs')
    model_config = relationship('ModelConfig', back_populates='call_logs')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'model_config_id': self.model_config_id,
            'provider': self.provider,
            'model_name': self.model_name,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'response_time': self.response_time,
            'is_success': self.is_success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ModelCallLog {self.id}: {self.provider}/{self.model_name}>'