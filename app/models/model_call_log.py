#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型调用日志相关模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, Text, DateTime, Boolean, JSON, Integer, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
import uuid

class CallStatus(str, enum.Enum):
    """调用状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"

class ModelCallLog(db.Model):
    """模型调用日志模型"""
    __tablename__ = 'model_call_logs'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_config_id = db.Column(String(36), ForeignKey('model_configs.id'), nullable=False, comment='模型配置ID')
    user_id = db.Column(String(36), comment='用户ID')
    session_id = db.Column(String(100), comment='会话ID')
    request_id = db.Column(String(100), comment='请求ID')
    
    # 请求信息
    input_text = db.Column(Text, comment='输入文本')
    input_messages = db.Column(JSON, comment='输入消息')
    request_params = db.Column(JSON, comment='请求参数')
    
    # 响应信息
    output_text = db.Column(Text, comment='输出文本')
    output_data = db.Column(JSON, comment='输出数据')
    
    # 调用状态
    status = db.Column(Enum(CallStatus), nullable=False, comment='调用状态')
    error_message = db.Column(Text, comment='错误信息')
    error_code = db.Column(String(50), comment='错误代码')
    
    # 统计信息
    input_tokens = db.Column(Integer, comment='输入令牌数')
    output_tokens = db.Column(Integer, comment='输出令牌数')
    total_tokens = db.Column(Integer, comment='总令牌数')
    duration = db.Column(Float, comment='调用耗时(秒)')
    estimated_cost = db.Column(Float, comment='预估成本')
    
    # 元数据
    metadata = db.Column(JSON, comment='元数据')
    
    # 时间字段
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创用时间')
    
    # 关系
    model_config = relationship("ModelConfig", back_populates="call_logs")
    
    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'model_config_id': self.model_config_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'request_id': self.request_id,
            'request_params': self.request_params or {},
            'status': self.status.value if self.status else None,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'duration': self.duration,
            'estimated_cost': self.estimated_cost,
            'metadata': self.metadata or {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # 敏感信息只在需要时包含
        if include_sensitive:
            data.update({
                'input_text': self.input_text,
                'input_messages': self.input_messages,
                'output_text': self.output_text,
                'output_data': self.output_data
            })
        
        return data
    
    def __repr__(self):
        return f'<ModelCallLog {self.request_id} - {self.status}>'