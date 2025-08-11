from sqlalchemy import BigInteger, String, Text, Integer, Float, DateTime, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import db
import uuid
import enum

class WorkflowStatus(str, enum.Enum):
    """工作流状态枚举"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class ActionType(str, enum.Enum):
    """用户行为类型枚举"""
    VIEW = "view"
    FORK = "fork"
    LIKE = "like"
    DOWNLOAD = "download"
    SHARE = "share"
    COMMENT = "comment"

class WorkflowCategory(str, enum.Enum):
    """工作流分类枚举"""
    AI_ASSISTANT = "ai_assistant"
    DATA_PROCESSING = "data_processing"
    AUTOMATION = "automation"
    CONTENT_CREATION = "content_creation"
    BUSINESS_PROCESS = "business_process"
    INTEGRATION = "integration"
    ANALYSIS = "analysis"
    OTHER = "other"

class Workflow(db.Model):
    """工作流模型"""
    __tablename__ = 'workflows'
    
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, comment='创建用户ID')
    name = db.Column(String(200), nullable=False, comment='工作流名称')
    description = db.Column(Text, comment='工作流描述')
    category = db.Column(String(50), default='general', comment='分类')
    tags = db.Column(JSON, comment='标签列表')
    
    version = db.Column(String(20), default='1.0.0', comment='版本号')
    status = db.Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT, comment='状态')
    is_public = db.Column(Boolean, default=False, comment='是否公开')
    canvas_config = db.Column(JSON, comment='画布配置信息')
    global_variables = db.Column(JSON, comment='全局变量配置')
    execution_timeout = db.Column(Integer, default=3600, comment='执行超时时间(秒)')
    max_concurrent_executions = db.Column(Integer, default=10, comment='最大并发执行数')
    
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    published_at = db.Column(DateTime, comment='发布时间')
    
    # 关联关系
    user = relationship("User")
    nodes = relationship("Node", back_populates="workflow", cascade="all, delete-orphan")
    connections = relationship("Connection", back_populates="workflow", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")
    reviews = relationship("WorkflowReview", back_populates="workflow", cascade="all, delete-orphan")
    stats = relationship("WorkflowStats", back_populates="workflow", cascade="all, delete-orphan")
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'tags': self.tags or [],
            'version': self.version,
            'status': self.status.value if self.status else None,
            'is_public': self.is_public,
            'canvas_config': self.canvas_config,
            'global_variables': self.global_variables,
            'execution_timeout': self.execution_timeout,
            'max_concurrent_executions': self.max_concurrent_executions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }

class WorkflowReview(db.Model):
    """工作流评价模型"""
    __tablename__ = 'workflow_reviews'
    
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String, db.ForeignKey('workflows.id'), nullable=False)
    user_id = db.Column(db.String, nullable=False)
    user_name = db.Column(db.String(100))
    
    # 评价内容
    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200))
    comment = db.Column(db.Text)
    
    # 有用性投票
    helpful_count = db.Column(db.Integer, default=0)
    unhelpful_count = db.Column(db.Integer, default=0)
    
    # 状态
    is_verified = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    # 时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    workflow = relationship("Workflow", back_populates="reviews")
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'helpful_count': self.helpful_count,
            'unhelpful_count': self.unhelpful_count,
            'is_verified': self.is_verified,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class WorkflowStats(db.Model):
    """工作流统计模型"""
    __tablename__ = 'workflow_stats'
    
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String, db.ForeignKey('workflows.id'), nullable=False)
    user_id = db.Column(db.String)
    action_type = db.Column(db.Enum(ActionType), nullable=False)
    
    # 额外信息
    extra_metadata = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    # 时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    workflow = relationship("Workflow", back_populates="stats")
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'user_id': self.user_id,
            'action_type': self.action_type.value if self.action_type else None,
            'extra_metadata': self.extra_metadata,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WorkflowCollection(db.Model):
    """工作流收藏模型"""
    __tablename__ = 'workflow_collections'
    
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String, db.ForeignKey('workflows.id'), nullable=False)
    user_id = db.Column(db.String, nullable=False)
    
    # 收藏信息
    collection_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    # 时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'user_id': self.user_id,
            'collection_name': self.collection_name,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WorkflowTag(db.Model):
    """工作流标签模型"""
    __tablename__ = 'workflow_tags'
    
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    color = db.Column(db.String(7))
    
    # 统计
    usage_count = db.Column(db.Integer, default=0)
    
    # 时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }