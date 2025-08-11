#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板和系统配置模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import BigInteger, String, Text, DateTime, Boolean, Integer, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

class WorkflowTemplate(db.Model):
    """工作流模板模型"""
    __tablename__ = 'workflow_templates'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(String(200), nullable=False, comment='模板名称')
    description = db.Column(Text, comment='模板描述')
    category = db.Column(String(50), comment='模板分类')
    tags = db.Column(String(500), comment='标签，用逗号分隔')
    template_data = db.Column(db.JSON, nullable=False, comment='模板数据')
    preview_image = db.Column(String(500), comment='预览图片URL')
    usage_count = db.Column(Integer, default=0, comment='使用次数')
    is_featured = db.Column(Boolean, default=False, comment='是否推荐')
    is_public = db.Column(Boolean, default=True, comment='是否公开')
    author_id = db.Column(BigInteger, ForeignKey('users.id'), comment='作者ID')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    author = relationship("User")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'tags': self.tags.split(',') if self.tags else [],
            'template_data': self.template_data,
            'preview_image': self.preview_image,
            'usage_count': self.usage_count,
            'is_featured': self.is_featured,
            'is_public': self.is_public,
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<WorkflowTemplate {self.name}>'

class SystemConfig(db.Model):
    """系统配置模型"""
    __tablename__ = 'system_configs'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    key = db.Column(String(100), unique=True, nullable=False, comment='配置键')
    value = db.Column(Text, comment='配置值')
    description = db.Column(String(500), comment='配置描述')
    data_type = db.Column(String(20), default='string', comment='数据类型')
    is_public = db.Column(Boolean, default=False, comment='是否公开')
    is_editable = db.Column(Boolean, default=True, comment='是否可编辑')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'data_type': self.data_type,
            'is_public': self.is_public,
            'is_editable': self.is_editable,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<SystemConfig {self.key}>'