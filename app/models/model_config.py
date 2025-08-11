#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型配置相关模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, Text, DateTime, Boolean, JSON, Integer, Float, Enum
from sqlalchemy.orm import relationship
import enum
import uuid

class ModelProvider(str, enum.Enum):
    """模型提供商枚举"""
    QWEN = "qwen"
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    BAIDU = "baidu"
    ZHIPU = "zhipu"
    CUSTOM = "custom"

class ModelType(str, enum.Enum):
    """模型类型枚举"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    IMAGE = "image"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"

class ModelConfig(db.Model):
    """AI模型配置模型"""
    __tablename__ = 'model_configs'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(String(100), unique=True, nullable=False, comment='配置名称')
    display_name = db.Column(String(200), comment='显示名称')
    description = db.Column(Text, comment='描述')
    
    # 模型信息
    provider = db.Column(Enum(ModelProvider), nullable=False, comment='模型提供商')
    model_type = db.Column(Enum(ModelType), nullable=False, comment='模型类型')
    model_name = db.Column(String(100), nullable=False, comment='模型名称')
    model_version = db.Column(String(50), comment='模型版本')
    
    # API配置
    api_endpoint = db.Column(String(500), comment='API端点')
    api_key = db.Column(String(500), comment='API密钥')
    api_secret = db.Column(String(500), comment='API密钥')
    
    # 模型参数
    max_tokens = db.Column(Integer, comment='最大令牌数')
    temperature = db.Column(Float, comment='温度参数')
    top_p = db.Column(Float, comment='Top-p参数')
    frequency_penalty = db.Column(Float, comment='频率惩罚')
    presence_penalty = db.Column(Float, comment='存在惩罚')
    
    # 扩展配置
    extra_config = db.Column(JSON, comment='扩展配置')
    
    # 限制配置
    rate_limit_rpm = db.Column(Integer, comment='每分钟请求限制')
    rate_limit_tpm = db.Column(Integer, comment='每分钟令牌限制')
    
    # 状态
    is_active = db.Column(Boolean, default=True, comment='是否激活')
    is_default = db.Column(Boolean, default=False, comment='是否默认配置')
    
    # 统计
    usage_count = db.Column(Integer, default=0, comment='使用次数')
    
    # 时间字段
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    usage_logs = relationship("ModelUsage", back_populates="model_config", cascade="all, delete-orphan")
    call_logs = relationship("ModelCallLog", back_populates="model_config", cascade="all, delete-orphan")
    
    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'provider': self.provider.value if self.provider else None,
            'model_type': self.model_type.value if self.model_type else None,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'api_endpoint': self.api_endpoint,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'extra_config': self.extra_config or {},
            'rate_limit_rpm': self.rate_limit_rpm,
            'rate_limit_tpm': self.rate_limit_tpm,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # 敏感信息只在需要时包含
        if include_sensitive:
            data.update({
                'api_key': self.api_key,
                'api_secret': self.api_secret
            })
        
        return data
    
    def __repr__(self):
        return f'<ModelConfig {self.name} - {self.provider}>'