#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型配置
"""

from datetime import datetime
from app.database import db

class ModelConfig(db.Model):
    """模型配置"""
    __tablename__ = 'model_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 模型配置名称
    model_type = db.Column(db.String(50), nullable=False)  # openai, qwen, claude, gemini, etc.
    provider = db.Column(db.String(50), nullable=False)  # 提供商：OpenAI, Alibaba, Anthropic, Google
    api_key = db.Column(db.String(255))  # API密钥
    api_base = db.Column(db.String(255))  # API基础URL
    model_name = db.Column(db.String(100))  # 具体模型名称
    max_tokens = db.Column(db.Integer, default=1000)  # 最大token数
    temperature = db.Column(db.Float, default=0.7)  # 温度参数
    top_p = db.Column(db.Float, default=1.0)  # top_p参数
    frequency_penalty = db.Column(db.Float, default=0.0)  # 频率惩罚
    presence_penalty = db.Column(db.Float, default=0.0)  # 存在惩罚
    system_prompt = db.Column(db.Text)  # 系统提示词
    enable_streaming = db.Column(db.Boolean, default=False)  # 是否启用流式输出
    timeout = db.Column(db.Integer, default=30)  # 超时时间(秒)
    description = db.Column(db.Text)  # 模型描述
    tags = db.Column(db.String(255))  # 标签，用逗号分隔
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)  # 是否公开给其他用户
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('model_configs', lazy=True))
    call_logs = db.relationship('ModelCallLog', back_populates='model_config', lazy=True)
    
    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type,
            'provider': self.provider,
            'api_base': self.api_base,
            'model_name': self.model_name,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'system_prompt': self.system_prompt,
            'enable_streaming': self.enable_streaming,
            'timeout': self.timeout,
            'description': self.description,
            'tags': self.tags.split(',') if self.tags else [],
            'user_id': self.user_id,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data['api_key'] = self.api_key
            
        return data
    
    def __repr__(self):
        return f'<ModelConfig {self.name}>'