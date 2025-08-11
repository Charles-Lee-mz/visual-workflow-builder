#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import BigInteger, String, Text, DateTime, Boolean, Integer, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

class WorkflowStatus(str, enum.Enum):
    """工作流状态枚举"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"

class ActionType(str, enum.Enum):
    """用户行为类型枚举"""
    VIEW = "view"
    LIKE = "like"
    FORK = "fork"
    COMMENT = "comment"
    SHARE = "share"

class WorkflowCategory(str, enum.Enum):
    """工作流分类枚举"""
    DATA_PROCESSING = "data_processing"
    API_INTEGRATION = "api_integration"
    AUTOMATION = "automation"
    AI_ML = "ai_ml"
    NOTIFICATION = "notification"
    FILE_PROCESSING = "file_processing"
    DATABASE = "database"
    WEB_SCRAPING = "web_scraping"
    BUSINESS_LOGIC = "business_logic"
    OTHER = "other"

class Workflow(db.Model):
    """工作流模型"""
    __tablename__ = 'workflows'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(String(200), nullable=False, comment='工作流名称')
    description = db.Column(Text, comment='工作流描述')
    category = db.Column(Enum(WorkflowCategory), default=WorkflowCategory.OTHER, comment='工作流分类')
    tags = db.Column(String(500), comment='标签，用逗号分隔')
    version = db.Column(String(20), default='1.0.0', comment='版本号')
    status = db.Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT, comment='工作流状态')
    is_public = db.Column(Boolean, default=False, comment='是否公开')
    canvas_config = db.Column(db.JSON, comment='画布配置')
    global_variables = db.Column(db.JSON, comment='全局变量')
    execution_timeout = db.Column(Integer, default=300, comment='执行超时时间(秒)')
    max_concurrent_executions = db.Column(Integer, default=1, comment='最大并发执行数')
    user_id = db.Column(BigInteger, ForeignKey('users.id'), nullable=False, comment='创建用户ID')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    published_at = db.Column(DateTime, comment='发布时间')
    
    # 关系
    user = relationship("User")
    nodes = relationship("Node", back_populates="workflow", cascade="all, delete-orphan")
    connections = relationship("Connection", back_populates="workflow", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", back_populates="workflow")
    reviews = relationship("WorkflowReview", back_populates="workflow")
    stats = relationship("WorkflowStats", back_populates="workflow", uselist=False)
    
    def to_dict(self, include_nodes=False, include_connections=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value if self.category else None,
            'tags': self.tags.split(',') if self.tags else [],
            'version': self.version,
            'status': self.status.value if self.status else None,
            'is_public': self.is_public,
            'canvas_config': self.canvas_config,
            'global_variables': self.global_variables,
            'execution_timeout': self.execution_timeout,
            'max_concurrent_executions': self.max_concurrent_executions,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
        
        if include_nodes:
            data['nodes'] = [node.to_dict() for node in self.nodes]
            
        if include_connections:
            data['connections'] = [conn.to_dict() for conn in self.connections]
            
        return data
    
    def __repr__(self):
        return f'<Workflow {self.name}>'

class WorkflowReview(db.Model):
    """工作流评价模型"""
    __tablename__ = 'workflow_reviews'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    workflow_id = db.Column(BigInteger, ForeignKey('workflows.id'), nullable=False)
    user_id = db.Column(BigInteger, ForeignKey('users.id'), nullable=False)
    rating = db.Column(Integer, nullable=False, comment='评分(1-5)')
    comment = db.Column(Text, comment='评价内容')
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # 关系
    workflow = relationship("Workflow", back_populates="reviews")
    user = relationship("User")
    
    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WorkflowStats(db.Model):
    """工作流统计模型"""
    __tablename__ = 'workflow_stats'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    workflow_id = db.Column(BigInteger, ForeignKey('workflows.id'), nullable=False)
    view_count = db.Column(Integer, default=0, comment='查看次数')
    like_count = db.Column(Integer, default=0, comment='点赞次数')
    fork_count = db.Column(Integer, default=0, comment='复制次数')
    execution_count = db.Column(Integer, default=0, comment='执行次数')
    success_rate = db.Column(Float, default=0.0, comment='成功率')
    avg_execution_time = db.Column(Float, default=0.0, comment='平均执行时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    workflow = relationship("Workflow", back_populates="stats")
    
    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'fork_count': self.fork_count,
            'execution_count': self.execution_count,
            'success_rate': self.success_rate,
            'avg_execution_time': self.avg_execution_time,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class WorkflowCollection(db.Model):
    """工作流收藏模型"""
    __tablename__ = 'workflow_collections'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(BigInteger, ForeignKey('users.id'), nullable=False)
    workflow_id = db.Column(BigInteger, ForeignKey('workflows.id'), nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User")
    workflow = relationship("Workflow")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'workflow_id': self.workflow_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WorkflowTag(db.Model):
    """工作流标签模型"""
    __tablename__ = 'workflow_tags'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(String(50), unique=True, nullable=False, comment='标签名称')
    description = db.Column(String(200), comment='标签描述')
    color = db.Column(String(7), comment='标签颜色')
    usage_count = db.Column(Integer, default=0, comment='使用次数')
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }