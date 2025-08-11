#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行模型
"""

from datetime import datetime
from app.database import db

class Execution(db.Model):
    """执行模型"""
    __tablename__ = 'executions'
    
    id = db.Column(db.Integer, primary_key=True)
    intent_id = db.Column(db.Integer, db.ForeignKey('intents.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    input_data = db.Column(db.JSON)
    output_data = db.Column(db.JSON)
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    intent = db.relationship('Intent', backref=db.backref('executions', lazy=True))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'intent_id': self.intent_id,
            'status': self.status,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Execution {self.id} - {self.status}>'

# WorkflowExecution 模型已移动到 workflow_execution.py 文件中