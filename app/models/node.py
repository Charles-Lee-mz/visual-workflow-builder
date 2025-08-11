#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节点相关模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import BigInteger, String, Text, DateTime, Boolean, JSON, Integer, Enum, ForeignKey
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
import enum
import uuid

class Node(db.Model):
    """节点模型"""
    __tablename__ = 'nodes'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(String(36), ForeignKey('workflows.id'), nullable=False, comment='所属工作流ID')
    node_id = db.Column(String(100), nullable=False, comment='节点唯一标识')
    node_type = db.Column(String(50), nullable=False, comment='节点类型')
    name = db.Column(String(200), nullable=False, comment='节点名称')
    description = db.Column(Text, comment='节点描述')
    position_x = db.Column(Numeric(10, 2), nullable=False, comment='X坐标')
    position_y = db.Column(Numeric(10, 2), nullable=False, comment='Y坐标')
    width = db.Column(Numeric(8, 2), default=200.00, comment='节点宽度')
    height = db.Column(Numeric(8, 2), default=100.00, comment='节点高度')
    config = db.Column(JSON, nullable=False, comment='节点配置')
    input_schema = db.Column(JSON, comment='输入参数模式')
    output_schema = db.Column(JSON, comment='输出参数模式')
    validation_rules = db.Column(JSON, comment='验证规则')
    is_start_node = db.Column(Boolean, default=False, comment='是否为开始节点')
    is_end_node = db.Column(Boolean, default=False, comment='是否为结束节点')
    retry_count = db.Column(Integer, default=0, comment='重试次数')
    timeout_seconds = db.Column(Integer, default=300, comment='超时时间(秒)')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    workflow = relationship("Workflow", back_populates="nodes")
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('workflow_id', 'node_id', name='uk_workflow_node'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'node_id': self.node_id,
            'node_type': self.node_type,
            'name': self.name,
            'description': self.description,
            'position_x': float(self.position_x) if self.position_x else None,
            'position_y': float(self.position_y) if self.position_y else None,
            'width': float(self.width) if self.width else None,
            'height': float(self.height) if self.height else None,
            'config': self.config,
            'input_schema': self.input_schema,
            'output_schema': self.output_schema,
            'validation_rules': self.validation_rules,
            'is_start_node': self.is_start_node,
            'is_end_node': self.is_end_node,
            'retry_count': self.retry_count,
            'timeout_seconds': self.timeout_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Node {self.node_id} - {self.name}>'

class ConnectionType(str, enum.Enum):
    """连接类型枚举"""
    DATA = "data"
    CONTROL = "control"

class Connection(db.Model):
    """连接线模型"""
    __tablename__ = 'connections'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(String(36), ForeignKey('workflows.id'), nullable=False, comment='所属工作流ID')
    connection_id = db.Column(String(100), nullable=False, comment='连接线唯一标识')
    source_node_id = db.Column(String(100), nullable=False, comment='源节点ID')
    source_handle = db.Column(String(100), comment='源节点输出端口')
    target_node_id = db.Column(String(100), nullable=False, comment='目标节点ID')
    target_handle = db.Column(String(100), comment='目标节点输入端口')
    connection_type = db.Column(Enum(ConnectionType), default=ConnectionType.DATA, comment='连接类型')
    condition_config = db.Column(JSON, comment='条件配置')
    style_config = db.Column(JSON, comment='样式配置')
    is_active = db.Column(Boolean, default=True, comment='是否激活')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    workflow = relationship("Workflow", back_populates="connections")
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('workflow_id', 'connection_id', name='uk_workflow_connection'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'connection_id': self.connection_id,
            'source_node_id': self.source_node_id,
            'source_handle': self.source_handle,
            'target_node_id': self.target_node_id,
            'target_handle': self.target_handle,
            'connection_type': self.connection_type.value if self.connection_type else None,
            'condition_config': self.condition_config,
            'style_config': self.style_config,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Connection {self.connection_id}: {self.source_node_id} -> {self.target_node_id}>'

class NodeType(db.Model):
    """节点类型定义模型"""
    __tablename__ = 'node_types'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type_name = db.Column(String(50), unique=True, nullable=False, comment='节点类型名称')
    display_name = db.Column(String(100), nullable=False, comment='显示名称')
    category = db.Column(String(50), nullable=False, comment='分类')
    description = db.Column(Text, comment='描述')
    icon_url = db.Column(String(500), comment='图标URL')
    color = db.Column(String(20), comment='主题颜色')
    default_config = db.Column(JSON, comment='默认配置')
    input_schema = db.Column(JSON, comment='输入参数模式')
    output_schema = db.Column(JSON, comment='输出参数模式')
    form_schema = db.Column(JSON, comment='表单配置模式')
    validation_rules = db.Column(JSON, comment='验证规则')
    is_system = db.Column(Boolean, default=True, comment='是否系统内置')
    is_active = db.Column(Boolean, default=True, comment='是否激活')
    version = db.Column(String(20), default='1.0.0', comment='版本号')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'type_name': self.type_name,
            'display_name': self.display_name,
            'category': self.category,
            'description': self.description,
            'icon_url': self.icon_url,
            'color': self.color,
            'default_config': self.default_config,
            'input_schema': self.input_schema,
            'output_schema': self.output_schema,
            'form_schema': self.form_schema,
            'validation_rules': self.validation_rules,
            'is_system': self.is_system,
            'is_active': self.is_active,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<NodeType {self.type_name} - {self.display_name}>'