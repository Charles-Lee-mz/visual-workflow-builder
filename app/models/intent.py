#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
意图识别相关模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, Text, DateTime, Boolean, JSON, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
import uuid

class Intent(db.Model):
    """意图模型"""
    __tablename__ = 'intents'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(String(100), unique=True, nullable=False, comment='意图名称')
    display_name = db.Column(String(200), comment='显示名称')
    description = db.Column(Text, comment='意图描述')
    category = db.Column(String(50), comment='意图分类')
    
    # 训练数据
    training_phrases = db.Column(JSON, comment='训练短语列表')
    parameters = db.Column(JSON, comment='参数定义')
    responses = db.Column(JSON, comment='响应模板')
    
    # 配置
    confidence_threshold = db.Column(Float, default=0.7, comment='置信度阈值')
    is_active = db.Column(Boolean, default=True, comment='是否激活')
    priority = db.Column(Integer, default=0, comment='优先级')
    
    # 统计
    match_count = db.Column(Integer, default=0, comment='匹配次数')
    success_rate = db.Column(Float, default=0.0, comment='成功率')
    
    # 时间字段
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    intent_logs = relationship("IntentLog", back_populates="intent", cascade="all, delete-orphan")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'category': self.category,
            'training_phrases': self.training_phrases or [],
            'parameters': self.parameters or {},
            'responses': self.responses or [],
            'confidence_threshold': self.confidence_threshold,
            'is_active': self.is_active,
            'priority': self.priority,
            'match_count': self.match_count,
            'success_rate': self.success_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Intent {self.name} - {self.display_name}>'

class IntentLog(db.Model):
    """意图识别日志模型"""
    __tablename__ = 'intent_logs'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    intent_id = db.Column(String(36), ForeignKey('intents.id'), comment='意图ID')
    user_input = db.Column(Text, nullable=False, comment='用户输入')
    detected_intent = db.Column(String(100), comment='检测到的意图')
    confidence_score = db.Column(Float, comment='置信度分数')
    extracted_parameters = db.Column(JSON, comment='提取的参数')
    response_text = db.Column(Text, comment='响应文本')
    is_correct = db.Column(Boolean, comment='是否正确识别')
    user_feedback = db.Column(String(20), comment='用户反馈')
    session_id = db.Column(String(100), comment='会话ID')
    user_id = db.Column(String(36), comment='用户ID')
    processing_time = db.Column(Float, comment='处理时间(毫秒)')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关系
    intent = relationship("Intent", back_populates="intent_logs")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'intent_id': self.intent_id,
            'user_input': self.user_input,
            'detected_intent': self.detected_intent,
            'confidence_score': self.confidence_score,
            'extracted_parameters': self.extracted_parameters or {},
            'response_text': self.response_text,
            'is_correct': self.is_correct,
            'user_feedback': self.user_feedback,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<IntentLog {self.detected_intent} - {self.confidence_score}>'