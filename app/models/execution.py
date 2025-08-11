#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行相关模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, Text, DateTime, Boolean, JSON, Integer, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
import enum
import uuid

class ExecutionStatus(str, enum.Enum):
    """执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class WorkflowExecution(db.Model):
    """工作流执行记录模型"""
    __tablename__ = 'workflow_executions'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(String(36), ForeignKey('workflows.id'), nullable=False, comment='工作流ID')
    user_id = db.Column(String(36), nullable=False, comment='执行用户ID')
    execution_name = db.Column(String(200), comment='执行名称')
    status = db.Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, comment='执行状态')
    input_data = db.Column(JSON, comment='输入数据')
    output_data = db.Column(JSON, comment='输出数据')
    error_message = db.Column(Text, comment='错误信息')
    execution_log = db.Column(Text, comment='执行日志')
    start_time = db.Column(DateTime, comment='开始时间')
    end_time = db.Column(DateTime, comment='结束时间')
    duration = db.Column(Float, comment='执行时长(秒)')
    progress = db.Column(Integer, default=0, comment='执行进度(0-100)')
    current_node_id = db.Column(String(100), comment='当前执行节点ID')
    execution_context = db.Column(JSON, comment='执行上下文')
    retry_count = db.Column(Integer, default=0, comment='重试次数')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    workflow = relationship("Workflow", back_populates="executions")
    node_executions = relationship("NodeExecution", back_populates="workflow_execution", cascade="all, delete-orphan")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'user_id': self.user_id,
            'execution_name': self.execution_name,
            'status': self.status.value if self.status else None,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'error_message': self.error_message,
            'execution_log': self.execution_log,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'progress': self.progress,
            'current_node_id': self.current_node_id,
            'execution_context': self.execution_context,
            'retry_count': self.retry_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<WorkflowExecution {self.id} - {self.status}>'

class NodeExecution(db.Model):
    """节点执行记录模型"""
    __tablename__ = 'node_executions'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_execution_id = db.Column(String(36), ForeignKey('workflow_executions.id'), nullable=False, comment='工作流执行ID')
    node_id = db.Column(String(100), nullable=False, comment='节点ID')
    node_type = db.Column(String(50), nullable=False, comment='节点类型')
    status = db.Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, comment='执行状态')
    input_data = db.Column(JSON, comment='输入数据')
    output_data = db.Column(JSON, comment='输出数据')
    error_message = db.Column(Text, comment='错误信息')
    execution_log = db.Column(Text, comment='执行日志')
    start_time = db.Column(DateTime, comment='开始时间')
    end_time = db.Column(DateTime, comment='结束时间')
    duration = db.Column(Float, comment='执行时长(秒)')
    retry_count = db.Column(Integer, default=0, comment='重试次数')
    execution_order = db.Column(Integer, comment='执行顺序')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    workflow_execution = relationship("WorkflowExecution", back_populates="node_executions")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'workflow_execution_id': self.workflow_execution_id,
            'node_id': self.node_id,
            'node_type': self.node_type,
            'status': self.status.value if self.status else None,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'error_message': self.error_message,
            'execution_log': self.execution_log,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'retry_count': self.retry_count,
            'execution_order': self.execution_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<NodeExecution {self.node_id} - {self.status}>'