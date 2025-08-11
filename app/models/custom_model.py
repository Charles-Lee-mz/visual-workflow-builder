#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义模型相关模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, Text, DateTime, Boolean, JSON, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
import uuid

class CustomModelStatus(str, enum.Enum):
    """自定义模型状态枚举"""
    DRAFT = "draft"
    TRAINING = "training"
    READY = "ready"
    FAILED = "failed"
    ARCHIVED = "archived"

class CustomModelType(str, enum.Enum):
    """自定义模型类型枚举"""
    FINE_TUNED = "fine_tuned"
    PROMPT_TEMPLATE = "prompt_template"
    FUNCTION_CALLING = "function_calling"
    RAG = "rag"

class CustomModel(db.Model):
    """自定义模型模型"""
    __tablename__ = 'custom_models'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(String(36), nullable=False, comment='创建用户ID')
    name = db.Column(String(100), nullable=False, comment='模型名称')
    display_name = db.Column(String(200), comment='显示名称')
    description = db.Column(Text, comment='模型描述')
    
    # 模型信息
    model_type = db.Column(Enum(CustomModelType), nullable=False, comment='模型类型')
    base_model_id = db.Column(String(36), ForeignKey('model_configs.id'), comment='基础模型ID')
    version = db.Column(String(20), default='1.0.0', comment='版本号')
    status = db.Column(Enum(CustomModelStatus), default=CustomModelStatus.DRAFT, comment='状态')
    
    # 配置信息
    model_config = db.Column(JSON, comment='模型配置')
    training_config = db.Column(JSON, comment='训练配置')
    prompt_template = db.Column(Text, comment='提示词模板')
    system_prompt = db.Column(Text, comment='系统提示词')
    
    # 训练数据
    training_data = db.Column(JSON, comment='训练数据')
    validation_data = db.Column(JSON, comment='验证数据')
    
    # 性能指标
    accuracy = db.Column(db.Float, comment='准确率')
    loss = db.Column(db.Float, comment='损失值')
    training_progress = db.Column(Integer, default=0, comment='训练进度(0-100)')
    
    # 部署信息
    deployment_config = db.Column(JSON, comment='部署配置')
    api_endpoint = db.Column(String(500), comment='API端点')
    
    # 状态
    is_public = db.Column(Boolean, default=False, comment='是否公开')
    is_active = db.Column(Boolean, default=True, comment='是否激活')
    
    # 统计
    usage_count = db.Column(Integer, default=0, comment='使用次数')
    
    # 时间字段
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    trained_at = db.Column(DateTime, comment='训练完成时间')
    
    # 关系
    base_model = relationship("ModelConfig", foreign_keys=[base_model_id])
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'model_type': self.model_type.value if self.model_type else None,
            'base_model_id': self.base_model_id,
            'version': self.version,
            'status': self.status.value if self.status else None,
            'model_config': self.model_config or {},
            'training_config': self.training_config or {},
            'prompt_template': self.prompt_template,
            'system_prompt': self.system_prompt,
            'training_data': self.training_data or [],
            'validation_data': self.validation_data or [],
            'accuracy': self.accuracy,
            'loss': self.loss,
            'training_progress': self.training_progress,
            'deployment_config': self.deployment_config or {},
            'api_endpoint': self.api_endpoint,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'trained_at': self.trained_at.isoformat() if self.trained_at else None
        }
    
    def __repr__(self):
        return f'<CustomModel {self.name} - {self.status}>'

class ModelTrainingLog(db.Model):
    """模型训练日志模型"""
    __tablename__ = 'model_training_logs'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    custom_model_id = db.Column(String(36), ForeignKey('custom_models.id'), nullable=False, comment='自定义模型ID')
    epoch = db.Column(Integer, comment='训练轮次')
    step = db.Column(Integer, comment='训练步数')
    loss = db.Column(db.Float, comment='损失值')
    accuracy = db.Column(db.Float, comment='准确率')
    learning_rate = db.Column(db.Float, comment='学习率')
    log_message = db.Column(Text, comment='日志信息')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关系
    custom_model = relationship("CustomModel")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'custom_model_id': self.custom_model_id,
            'epoch': self.epoch,
            'step': self.step,
            'loss': self.loss,
            'accuracy': self.accuracy,
            'learning_rate': self.learning_rate,
            'log_message': self.log_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ModelTrainingLog {self.custom_model_id} - Epoch {self.epoch}>'

class ModelEvaluation(db.Model):
    """模型评估模型"""
    __tablename__ = 'model_evaluations'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    custom_model_id = db.Column(String(36), ForeignKey('custom_models.id'), nullable=False, comment='自定义模型ID')
    evaluation_name = db.Column(String(100), comment='评估名称')
    test_dataset = db.Column(JSON, comment='测试数据集')
    
    # 评估结果
    accuracy = db.Column(db.Float, comment='准确率')
    precision = db.Column(db.Float, comment='精确率')
    recall = db.Column(db.Float, comment='召回率')
    f1_score = db.Column(db.Float, comment='F1分数')
    
    # 详细结果
    evaluation_results = db.Column(JSON, comment='详细评估结果')
    confusion_matrix = db.Column(JSON, comment='混淆矩阵')
    
    # 时间字段
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关系
    custom_model = relationship("CustomModel")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'custom_model_id': self.custom_model_id,
            'evaluation_name': self.evaluation_name,
            'test_dataset': self.test_dataset or [],
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'evaluation_results': self.evaluation_results or {},
            'confusion_matrix': self.confusion_matrix or {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ModelEvaluation {self.custom_model_id} - {self.evaluation_name}>'

class ModelDeployment(db.Model):
    """模型部署模型"""
    __tablename__ = 'model_deployments'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    custom_model_id = db.Column(String(36), ForeignKey('custom_models.id'), nullable=False, comment='自定义模型ID')
    deployment_name = db.Column(String(100), nullable=False, comment='部署名称')
    
    # 部署配置
    deployment_config = db.Column(JSON, comment='部署配置')
    api_endpoint = db.Column(String(500), comment='API端点')
    api_key = db.Column(String(500), comment='API密钥')
    
    # 资源配置
    cpu_limit = db.Column(db.Float, comment='CPU限制')
    memory_limit = db.Column(Integer, comment='内存限制(MB)')
    gpu_count = db.Column(Integer, comment='GPU数量')
    
    # 状态
    status = db.Column(String(20), default='pending', comment='部署状态')
    is_active = db.Column(Boolean, default=True, comment='是否激活')
    
    # 统计
    request_count = db.Column(Integer, default=0, comment='请求次数')
    
    # 时间字段
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    deployed_at = db.Column(DateTime, comment='部署时间')
    
    # 关系
    custom_model = relationship("CustomModel")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'custom_model_id': self.custom_model_id,
            'deployment_name': self.deployment_name,
            'deployment_config': self.deployment_config or {},
            'api_endpoint': self.api_endpoint,
            'cpu_limit': self.cpu_limit,
            'memory_limit': self.memory_limit,
            'gpu_count': self.gpu_count,
            'status': self.status,
            'is_active': self.is_active,
            'request_count': self.request_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deployed_at': self.deployed_at.isoformat() if self.deployed_at else None
        }
    
    def __repr__(self):
        return f'<ModelDeployment {self.deployment_name} - {self.status}>'
