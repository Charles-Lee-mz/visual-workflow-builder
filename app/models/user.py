#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户模型
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db
from sqlalchemy import BigInteger, String, Text, DateTime, Boolean, Enum
import enum

class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(String(80), unique=True, nullable=False, comment='用户名')
    email = db.Column(String(120), unique=True, nullable=False, comment='邮箱')
    password_hash = db.Column(String(255), nullable=False, comment='密码哈希')
    display_name = db.Column(String(100), comment='显示名称')
    avatar_url = db.Column(String(500), comment='头像URL')
    role = db.Column(Enum(UserRole), default=UserRole.USER, comment='用户角色')
    status = db.Column(Enum(UserStatus), default=UserStatus.ACTIVE, comment='用户状态')
    last_login_at = db.Column(DateTime, comment='最后登录时间')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'avatar_url': self.avatar_url,
            'role': self.role.value if self.role else None,
            'status': self.status.value if self.status else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
            
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'