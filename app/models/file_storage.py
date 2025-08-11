#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件存储相关模型
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, Text, DateTime, Boolean, Integer, BigInteger, Enum, ForeignKey
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

class StorageProvider(str, enum.Enum):
    """存储提供商枚举"""
    LOCAL = "local"
    OSS = "oss"
    S3 = "s3"
    COS = "cos"

class FileStorage(db.Model):
    """文件存储模型"""
    __tablename__ = 'file_storage'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(String(36), nullable=False, comment='上传用户ID')
    original_name = db.Column(String(255), nullable=False, comment='原始文件名')
    stored_name = db.Column(String(255), nullable=False, comment='存储文件名')
    file_path = db.Column(String(500), nullable=False, comment='文件路径')
    file_url = db.Column(String(500), comment='访问URL')
    file_type = db.Column(Enum(FileType), nullable=False, comment='文件类型')
    mime_type = db.Column(String(100), comment='MIME类型')
    file_size = db.Column(BigInteger, nullable=False, comment='文件大小(字节)')
    file_hash = db.Column(String(64), comment='文件哈希值')
    storage_provider = db.Column(Enum(StorageProvider), default=StorageProvider.LOCAL, comment='存储提供商')
    bucket_name = db.Column(String(100), comment='存储桶名称')
    
    # 元数据
    metadata = db.Column(db.JSON, comment='文件元数据')
    
    # 状态
    is_public = db.Column(Boolean, default=False, comment='是否公开')
    is_temporary = db.Column(Boolean, default=False, comment='是否临时文件')
    expires_at = db.Column(DateTime, comment='过期时间')
    
    # 统计
    download_count = db.Column(Integer, default=0, comment='下载次数')
    
    # 时间字段
    created_at = db.Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_name': self.original_name,
            'stored_name': self.stored_name,
            'file_path': self.file_path,
            'file_url': self.file_url,
            'file_type': self.file_type.value if self.file_type else None,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'storage_provider': self.storage_provider.value if self.storage_provider else None,
            'bucket_name': self.bucket_name,
            'metadata': self.metadata or {},
            'is_public': self.is_public,
            'is_temporary': self.is_temporary,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<FileStorage {self.original_name} - {self.file_type}>'