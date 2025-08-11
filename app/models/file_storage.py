#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件存储模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import BigInteger, String, Text, DateTime, Boolean, Integer, Enum, ForeignKey
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
import enum
import uuid

class FileType(str, enum.Enum):
    """文件类型枚举"""
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    DATA = "data"
    OTHER = "other"

class FileStorage(db.Model):
    """文件存储模型"""
    __tablename__ = 'file_uploads'
    
    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    file_id = db.Column(String(100), unique=True, nullable=False, comment='文件唯一标识')
    user_id = db.Column(BigInteger, ForeignKey('users.id'), nullable=False, comment='上传用户ID')
    original_name = db.Column(String(500), nullable=False, comment='原始文件名')
    stored_name = db.Column(String(500), nullable=False, comment='存储文件名')
    file_path = db.Column(String(1000), nullable=False, comment='文件路径')
    file_type = db.Column(Enum(FileType), nullable=False, comment='文件类型')
    file_extension = db.Column(String(20), comment='文件扩展名')
    file_size = db.Column(BigInteger, nullable=False, comment='文件大小(字节)')
    mime_type = db.Column(String(200), comment='MIME类型')
    checksum = db.Column(String(64), comment='文件校验和')
    description = db.Column(Text, comment='文件描述')
    file_metadata = db.Column(db.JSON, comment='文件元数据')
    is_public = db.Column(Boolean, default=False, comment='是否公开')
    is_deleted = db.Column(Boolean, default=False, comment='是否已删除')
    download_count = db.Column(Integer, default=0, comment='下载次数')
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    user = relationship("User")
    
    def __init__(self, **kwargs):
        super(FileStorage, self).__init__(**kwargs)
        if not self.file_id:
            self.file_id = str(uuid.uuid4())
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'file_id': self.file_id,
            'user_id': self.user_id,
            'original_name': self.original_name,
            'stored_name': self.stored_name,
            'file_path': self.file_path,
            'file_type': self.file_type.value if self.file_type else None,
            'file_extension': self.file_extension,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'checksum': self.checksum,
            'description': self.description,
            'file_metadata': self.file_metadata,
            'is_public': self.is_public,
            'is_deleted': self.is_deleted,
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<FileStorage {self.file_id} - {self.original_name}>'