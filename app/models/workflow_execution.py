#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流执行相关模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, Text, DateTime, Boolean, JSON, Integer, Float, Enum, ForeignKey
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
    PAUSED = "paused"

class ExecutionTrigger(str, enum.Enum):
    """执行触发方式枚举"""
    MANUAL = "manual"
    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    API = "api"
    EVENT = "event"

class WorkflowExecution(db.Model):
    """工作流执行模型"""
    __tablename__ = 'workflow_executions'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(String(36), ForeignKey('workflows.id'), nullable=False, comment='工作流ID')
    user_id = db.Column(String(36), comment='执行用户ID')
    execution_name = db.Column(String(200), comment='执行名称')
    
    # 执行信息
    status = db.Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, comment='执行状态')
    trigger_type = db.Column(Enum(ExecutionTrigger), default=ExecutionTrigger.MANUAL, comment='触发方式')
    trigger_data = db.Column(JSON, comment='触发数据')
    
    # 输入输出
    input_data = db.Column(JSON, comment='输入数据')
    output_data = db.Column(JSON, comment='输出数据')
    context_data = db.Column(JSON, comment='上下文数据')
    
    # 执行配置
    execution_config = db.Column(JSON, comment='执行配置')
    timeout_seconds = db.Column(Integer, comment='超时时间(秒)')
    max_retries = db.Column(Integer, default=0, comment='最大重试次数')
    retry_count = db.Column(Integer, default=0, comment='当前重试次数')
    
    # 执行统计
    total_nodes = db.Column(Integer, default=0, comment='总节点数')
    completed_nodes = db.Column(Integer, default=0, comment='已完成节点数')
    failed_nodes = db.Column(Integer, default=0, comment='失败节点数')
    skipped_nodes = db.Column(Integer, default=0, comment='跳过节点数')
    
    # 时间统计
    started_at = db.Column(DateTime, comment='开始时间')
    completed_at = db.Column(DateTime, comment='完成时间')
    duration = db.Column(Float, comment='执行时长(秒)')
    
    # 错误信息
    error_message = db.Column(Text, comment='错误信息')
    error_details = db.Column(JSON, comment='错误详情')
    
    # 执行日志
    execution_log = db.Column(Text, comment='执行日志')
    
    # 资源使用
    cpu_usage = db.Column(Float, comment='CPU使用率')
    memory_usage = db.Column(Float, comment='内存使用量(MB)')
    
    # 优先级
    priority = db.Column(Integer, default=0, comment='执行优先级')
    
    # 标签
    tags = db.Column(JSON, comment='标签')
    
    # 时间字段
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
            'trigger_type': self.trigger_type.value if self.trigger_type else None,
            'trigger_data': self.trigger_data or {},
            'input_data': self.input_data or {},
            'output_data': self.output_data or {},
            'context_data': self.context_data or {},
            'execution_config': self.execution_config or {},
            'timeout_seconds': self.timeout_seconds,
            'max_retries': self.max_retries,
            'retry_count': self.retry_count,
            'total_nodes': self.total_nodes,
            'completed_nodes': self.completed_nodes,
            'failed_nodes': self.failed_nodes,
            'skipped_nodes': self.skipped_nodes,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration,
            'error_message': self.error_message,
            'error_details': self.error_details or {},
            'execution_log': self.execution_log,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'priority': self.priority,
            'tags': self.tags or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<WorkflowExecution {self.id} - {self.status}>'

class NodeExecution(db.Model):
    """节点执行模型"""
    __tablename__ = 'node_executions'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_execution_id = db.Column(String(36), ForeignKey('workflow_executions.id'), nullable=False, comment='工作流执行ID')
    node_id = db.Column(String(36), ForeignKey('nodes.id'), nullable=False, comment='节点ID')
    node_key = db.Column(String(100), comment='节点唯一标识')
    
    # 执行信息
    status = db.Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, comment='执行状态')
    execution_order = db.Column(Integer, comment='执行顺序')
    
    # 输入输出
    input_data = db.Column(JSON, comment='输入数据')
    output_data = db.Column(JSON, comment='输出数据')
    
    # 时间统计
    started_at = db.Column(DateTime, comment='开始时间')
    completed_at = db.Column(DateTime, comment='完成时间')
    duration = db.Column(Float, comment='执行时长(秒)')
    
    # 重试信息
    retry_count = db.Column(Integer, default=0, comment='重试次数')
    max_retries = db.Column(Integer, default=0, comment='最大重试次数')
    
    # 错误信息
    error_message = db.Column(Text, comment='错误信息')
    error_details = db.Column(JSON, comment='错误详情')
    
    # 执行日志
    execution_log = db.Column(Text, comment='执行日志')
    
    # 资源使用
    cpu_usage = db.Column(Float, comment='CPU使用率')
    memory_usage = db.Column(Float, comment='内存使用量(MB)')
    
    # 时间字段
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
            'node_key': self.node_key,
            'status': self.status.value if self.status else None,
            'execution_order': self.execution_order,
            'input_data': self.input_data or {},
            'output_data': self.output_data or {},
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'error_message': self.error_message,
            'error_details': self.error_details or {},
            'execution_log': self.execution_log,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<NodeExecution {self.node_key} - {self.status}>'

class ExecutionSchedule(db.Model):
    """执行调度模型"""
    __tablename__ = 'execution_schedules'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(String(36), ForeignKey('workflows.id'), nullable=False, comment='工作流ID')
    user_id = db.Column(String(36), comment='创建用户ID')
    schedule_name = db.Column(String(200), comment='调度名称')
    
    # 调度配置
    cron_expression = db.Column(String(100), comment='Cron表达式')
    timezone = db.Column(String(50), default='UTC', comment='时区')
    
    # 执行配置
    input_data = db.Column(JSON, comment='输入数据')
    execution_config = db.Column(JSON, comment='执行配置')
    
    # 状态
    is_active = db.Column(Boolean, default=True, comment='是否激活')
    
    # 统计
    execution_count = db.Column(Integer, default=0, comment='执行次数')
    success_count = db.Column(Integer, default=0, comment='成功次数')
    failure_count = db.Column(Integer, default=0, comment='失败次数')
    
    # 时间字段
    next_run_time = db.Column(DateTime, comment='下次执行时间')
    last_run_time = db.Column(DateTime, comment='上次执行时间')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    workflow = relationship("Workflow")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'user_id': self.user_id,
            'schedule_name': self.schedule_name,
            'cron_expression': self.cron_expression,
            'timezone': self.timezone,
            'input_data': self.input_data or {},
            'execution_config': self.execution_config or {},
            'is_active': self.is_active,
            'execution_count': self.execution_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ExecutionSchedule {self.schedule_name} - {self.cron_expression}>'

class ExecutionWebhook(db.Model):
    """执行Webhook模型"""
    __tablename__ = 'execution_webhooks'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(String(36), ForeignKey('workflows.id'), nullable=False, comment='工作流ID')
    user_id = db.Column(String(36), comment='创建用户ID')
    webhook_name = db.Column(String(200), comment='Webhook名称')
    
    # Webhook配置
    webhook_url = db.Column(String(500), unique=True, comment='Webhook URL')
    secret_token = db.Column(String(100), comment='密钥令牌')
    
    # 触发配置
    trigger_events = db.Column(JSON, comment='触发事件')
    filter_conditions = db.Column(JSON, comment='过滤条件')
    
    # 执行配置
    input_mapping = db.Column(JSON, comment='输入映射')
    execution_config = db.Column(JSON, comment='执行配置')
    
    # 状态
    is_active = db.Column(Boolean, default=True, comment='是否激活')
    
    # 统计
    trigger_count = db.Column(Integer, default=0, comment='触发次数')
    success_count = db.Column(Integer, default=0, comment='成功次数')
    failure_count = db.Column(Integer, default=0, comment='失败次数')
    
    # 时间字段
    last_triggered_at = db.Column(DateTime, comment='上次触发时间')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    workflow = relationship("Workflow")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'user_id': self.user_id,
            'webhook_name': self.webhook_name,
            'webhook_url': self.webhook_url,
            'secret_token': self.secret_token,
            'trigger_events': self.trigger_events or [],
            'filter_conditions': self.filter_conditions or {},
            'input_mapping': self.input_mapping or {},
            'execution_config': self.execution_config or {},
            'is_active': self.is_active,
            'trigger_count': self.trigger_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'last_triggered_at': self.last_triggered_at.isoformat() if self.last_triggered_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ExecutionWebhook {self.webhook_name} - {self.webhook_url}>'
