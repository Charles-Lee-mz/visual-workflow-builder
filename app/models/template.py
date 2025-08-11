#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板相关模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, Text, DateTime, Boolean, JSON, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
import uuid

class TemplateStatus(str, enum.Enum):
    """模板状态枚举"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class TemplateCategory(str, enum.Enum):
    """模板分类枚举"""
    AI_ASSISTANT = "ai_assistant"
    DATA_PROCESSING = "data_processing"
    AUTOMATION = "automation"
    CONTENT_CREATION = "content_creation"
    BUSINESS_PROCESS = "business_process"
    INTEGRATION = "integration"
    ANALYSIS = "analysis"
    OTHER = "other"

class Template(db.Model):
    """工作流模板模型"""
    __tablename__ = 'templates'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(String(200), nullable=False, comment='模板名称')
    description = db.Column(Text, comment='模板描述')
    category = db.Column(Enum(TemplateCategory), default=TemplateCategory.OTHER, comment='分类')
    tags = db.Column(JSON, comment='标签列表')
    author_id = db.Column(String(36), nullable=False, comment='作者ID')
    author_name = db.Column(String(100), comment='作者名称')
    version = db.Column(String(20), default='1.0.0', comment='版本号')
    status = db.Column(Enum(TemplateStatus), default=TemplateStatus.DRAFT, comment='状态')
    is_featured = db.Column(Boolean, default=False, comment='是否精选')
    is_official = db.Column(Boolean, default=False, comment='是否官方模板')
    
    # 模板内容
    workflow_config = db.Column(JSON, nullable=False, comment='工作流配置')
    preview_image = db.Column(String(500), comment='预览图片URL')
    demo_data = db.Column(JSON, comment='演示数据')
    
    # 统计信息
    download_count = db.Column(Integer, default=0, comment='下载次数')
    like_count = db.Column(Integer, default=0, comment='点赞次数')
    view_count = db.Column(Integer, default=0, comment='查看次数')
    rating_average = db.Column(db.Float, default=0.0, comment='平均评分')
    rating_count = db.Column(Integer, default=0, comment='评分次数')
    
    # 时间字段
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    published_at = db.Column(DateTime, comment='发布时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value if self.category else None,
            'tags': self.tags or [],
            'author_id': self.author_id,
            'author_name': self.author_name,
            'version': self.version,
            'status': self.status.value if self.status else None,
            'is_featured': self.is_featured,
            'is_official': self.is_official,
            'workflow_config': self.workflow_config,
            'preview_image': self.preview_image,
            'demo_data': self.demo_data,
            'download_count': self.download_count,
            'like_count': self.like_count,
            'view_count': self.view_count,
            'rating_average': self.rating_average,
            'rating_count': self.rating_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
    
    def __repr__(self):
        return f'<Template {self.name} - {self.status}>'