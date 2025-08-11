#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节点模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import BigInteger, String, Text, DateTime, Boolean, Integer, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

class Node(db.Model):
    """节点模型"""
    __tablename__ = 'nodes'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    workflow_id = db.Column(BigInteger, ForeignKey('workflows.id'), nullable=False, comment='所属工作流ID')
    node_type = db.Column(String(50), nullable=False, comment='节点类型')
    name = db.Column(String(200), nullable=False, comment='节点名称')
    description = db.Column(Text, comment='节点描述')
    position_x = db.Column(Float, default=0, comment='X坐标')
    position_y = db.Column(Float, default=0, comment='Y坐标')
    config = db.Column(db.JSON, comment='节点配置')
    input_schema = db.Column(db.JSON, comment='输入模式')
    output_schema = db.Column(db.JSON, comment='输出模式')
    validation_rules = db.Column(db.JSON, comment='验证规则')
    retry_count = db.Column(Integer, default=0, comment='重试次数')
    timeout = db.Column(Integer, default=30, comment='超时时间(秒)')
    is_enabled = db.Column(Boolean, default=True, comment='是否启用')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    workflow = relationship("Workflow", back_populates="nodes")
    input_connections = relationship("Connection", foreign_keys="Connection.target_node_id", back_populates="target_node")
    output_connections = relationship("Connection", foreign_keys="Connection.source_node_id", back_populates="source_node")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'node_type': self.node_type,
            'name': self.name,
            'description': self.description,
            'position': {
                'x': self.position_x,
                'y': self.position_y
            },
            'config': self.config,
            'input_schema': self.input_schema,
            'output_schema': self.output_schema,
            'validation_rules': self.validation_rules,
            'retry_count': self.retry_count,
            'timeout': self.timeout,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Node {self.name} ({self.node_type})>'

class Connection(db.Model):
    """连接线模型"""
    __tablename__ = 'connections'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    workflow_id = db.Column(BigInteger, ForeignKey('workflows.id'), nullable=False, comment='所属工作流ID')
    source_node_id = db.Column(BigInteger, ForeignKey('nodes.id'), nullable=False, comment='源节点ID')
    target_node_id = db.Column(BigInteger, ForeignKey('nodes.id'), nullable=False, comment='目标节点ID')
    source_handle = db.Column(String(100), comment='源节点输出端口')
    target_handle = db.Column(String(100), comment='目标节点输入端口')
    condition = db.Column(db.JSON, comment='连接条件')
    is_enabled = db.Column(Boolean, default=True, comment='是否启用')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关系
    workflow = relationship("Workflow", back_populates="connections")
    source_node = relationship("Node", foreign_keys=[source_node_id], back_populates="output_connections")
    target_node = relationship("Node", foreign_keys=[target_node_id], back_populates="input_connections")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'source_node_id': self.source_node_id,
            'target_node_id': self.target_node_id,
            'source_handle': self.source_handle,
            'target_handle': self.target_handle,
            'condition': self.condition,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Connection {self.source_node_id} -> {self.target_node_id}>'

class NodeType(db.Model):
    """节点类型模型"""
    __tablename__ = 'node_types'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(String(100), unique=True, nullable=False, comment='节点类型名称')
    display_name = db.Column(String(200), nullable=False, comment='显示名称')
    description = db.Column(Text, comment='节点描述')
    category = db.Column(String(50), comment='节点分类')
    icon = db.Column(String(100), comment='图标')
    color = db.Column(String(7), comment='颜色')
    config_schema = db.Column(db.JSON, comment='配置模式')
    input_schema = db.Column(db.JSON, comment='输入模式')
    output_schema = db.Column(db.JSON, comment='输出模式')
    is_builtin = db.Column(Boolean, default=False, comment='是否内置')
    is_enabled = db.Column(Boolean, default=True, comment='是否启用')
    version = db.Column(String(20), default='1.0.0', comment='版本号')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'category': self.category,
            'icon': self.icon,
            'color': self.color,
            'config_schema': self.config_schema,
            'input_schema': self.input_schema,
            'output_schema': self.output_schema,
            'is_builtin': self.is_builtin,
            'is_enabled': self.is_enabled,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<NodeType {self.name}>'