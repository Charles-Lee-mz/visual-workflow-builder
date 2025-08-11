#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流执行模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import BigInteger, String, Text, DateTime, Boolean, Integer, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

class ExecutionStatus(str, enum.Enum):
    """执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class TriggerType(str, enum.Enum):
    """触发类型枚举"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    WEBHOOK = "webhook"
    API = "api"
    EVENT = "event"

class WorkflowExecution(db.Model):
    """工作流执行模型"""
    __tablename__ = 'workflow_executions'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    workflow_id = db.Column(BigInteger, ForeignKey('workflows.id'), nullable=False, comment='工作流ID')
    user_id = db.Column(BigInteger, ForeignKey('users.id'), nullable=False, comment='执行用户ID')
    trigger_type = db.Column(Enum(TriggerType), default=TriggerType.MANUAL, comment='触发类型')
    input_data = db.Column(db.JSON, comment='输入数据')
    output_data = db.Column(db.JSON, comment='输出数据')
    status = db.Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, comment='执行状态')
    progress = db.Column(Float, default=0.0, comment='执行进度(0-100)')
    error_message = db.Column(Text, comment='错误信息')
    started_at = db.Column(DateTime, comment='开始时间')
    completed_at = db.Column(DateTime, comment='完成时间')
    duration = db.Column(Float, comment='执行时长(秒)')
    node_count = db.Column(Integer, default=0, comment='节点总数')
    completed_nodes = db.Column(Integer, default=0, comment='已完成节点数')
    failed_nodes = db.Column(Integer, default=0, comment='失败节点数')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    workflow = relationship("Workflow", back_populates="executions")
    user = relationship("User")
    node_executions = relationship("NodeExecution", back_populates="workflow_execution", cascade="all, delete-orphan")
    
    def to_dict(self, include_nodes=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'user_id': self.user_id,
            'trigger_type': self.trigger_type.value if self.trigger_type else None,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'status': self.status.value if self.status else None,
            'progress': self.progress,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration,
            'node_count': self.node_count,
            'completed_nodes': self.completed_nodes,
            'failed_nodes': self.failed_nodes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_nodes:
            data['node_executions'] = [node_exec.to_dict() for node_exec in self.node_executions]
            
        return data
    
    def __repr__(self):
        return f'<WorkflowExecution {self.id} - {self.status}>'

class NodeExecution(db.Model):
    """节点执行模型"""
    __tablename__ = 'node_executions'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    workflow_execution_id = db.Column(BigInteger, ForeignKey('workflow_executions.id'), nullable=False, comment='工作流执行ID')
    node_id = db.Column(BigInteger, ForeignKey('nodes.id'), nullable=False, comment='节点ID')
    status = db.Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, comment='执行状态')
    input_data = db.Column(db.JSON, comment='输入数据')
    output_data = db.Column(db.JSON, comment='输出数据')
    error_message = db.Column(Text, comment='错误信息')
    retry_count = db.Column(Integer, default=0, comment='重试次数')
    started_at = db.Column(DateTime, comment='开始时间')
    completed_at = db.Column(DateTime, comment='完成时间')
    duration = db.Column(Float, comment='执行时长(秒)')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    workflow_execution = relationship("WorkflowExecution", back_populates="node_executions")
    node = relationship("Node")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'workflow_execution_id': self.workflow_execution_id,
            'node_id': self.node_id,
            'status': self.status.value if self.status else None,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<NodeExecution {self.id} - {self.status}>'