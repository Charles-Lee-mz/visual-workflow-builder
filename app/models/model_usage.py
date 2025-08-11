#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型使用统计相关模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, Text, DateTime, Integer, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
import uuid

class ModelUsage(db.Model):
    """模型使用统计模型"""
    __tablename__ = 'model_usage'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_config_id = db.Column(String(36), ForeignKey('model_configs.id'), nullable=False, comment='模型配置ID')
    user_id = db.Column(String(36), comment='用户ID')
    date = db.Column(Date, nullable=False, comment='统计日期')
    
    # 使用统计
    request_count = db.Column(Integer, default=0, comment='请求次数')
    success_count = db.Column(Integer, default=0, comment='成功次数')
    error_count = db.Column(Integer, default=0, comment='错误次数')
    
    # 令牌统计
    input_tokens = db.Column(Integer, default=0, comment='输入令牌数')
    output_tokens = db.Column(Integer, default=0, comment='输出令牌数')
    total_tokens = db.Column(Integer, default=0, comment='总令牌数')
    
    # 时间统计
    total_duration = db.Column(Float, default=0.0, comment='总耗时(秒)')
    avg_duration = db.Column(Float, default=0.0, comment='平均耗时(秒)')
    
    # 成本统计
    estimated_cost = db.Column(Float, default=0.0, comment='预估成本')
    
    # 时间字段
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    model_config = relationship("ModelConfig", back_populates="usage_logs")
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('model_config_id', 'user_id', 'date', name='uk_model_usage_daily'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'model_config_id': self.model_config_id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'request_count': self.request_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'total_duration': self.total_duration,
            'avg_duration': self.avg_duration,
            'estimated_cost': self.estimated_cost,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ModelUsage {self.model_config_id} - {self.date}>'